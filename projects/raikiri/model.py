"""Raikiri model built from the official Intern-S2-Mobius code."""

import sys
from pathlib import Path

from config import DataConfig, ModelConfig


def resolve_attention_backend(requested, capability=None, flash_available=None):
    """Choose a safe backend; upstream FlashAttention-2 does not support T4."""
    supported = {"auto", "sdpa", "flash_attention_2", "flex_attention", "eager"}
    if requested not in supported:
        raise ValueError("attention_backend must be one of {}, got {!r}".format(sorted(supported), requested))
    if requested != "auto":
        return requested

    if capability is None:
        import torch

        capability = torch.cuda.get_device_capability() if torch.cuda.is_available() else (0, 0)
    if flash_available is None:
        try:
            from transformers.utils import is_flash_attn_2_available

            flash_available = is_flash_attn_2_available()
        except ImportError:
            flash_available = False

    return "flash_attention_2" if capability[0] >= 8 and flash_available else "sdpa"


def configure_model(config, tokenizer, model: ModelConfig, data: DataConfig, attention_backend):
    """Shrink the released architecture while preserving its defining structure."""
    if model.hidden_size != model.num_attention_heads * model.head_dim:
        raise ValueError("hidden_size must equal num_attention_heads * head_dim")
    if data.sequence_length < model.sliding_window:
        raise ValueError("sliding_window cannot exceed sequence_length")

    text = config.text_config
    values = {
        "vocab_size": len(tokenizer),
        "hidden_size": model.hidden_size,
        "num_hidden_layers": model.num_hidden_layers,
        "num_attention_heads": model.num_attention_heads,
        "num_key_value_heads": model.num_key_value_heads,
        "head_dim": model.head_dim,
        "max_position_embeddings": data.sequence_length,
        "num_blocks": model.num_memory_blocks,
        "num_experts": model.num_memory_experts,
        "num_experts_per_tok": model.experts_per_token,
        "moe_intermediate_size": model.expert_intermediate_size,
        "shared_expert_intermediate_size": model.local_expert_intermediate_size,
        "linear_key_head_dim": model.head_dim,
        "linear_value_head_dim": model.head_dim,
        "linear_num_key_heads": model.num_key_value_heads,
        "linear_num_value_heads": model.num_attention_heads,
        "sliding_window": model.sliding_window,
        "pad_token_id": tokenizer.pad_token_id,
        "bos_token_id": tokenizer.bos_token_id,
        "eos_token_id": tokenizer.eos_token_id,
        "tie_word_embeddings": True,
        "output_router_logits": True,
        "use_cache": False,
        "_attn_implementation": attention_backend,
    }
    for name, value in values.items():
        setattr(text, name, value)

    text.layer_types = [
        "full_attention" if (index + 1) % model.full_attention_every == 0 else "linear_attention"
        for index in range(model.num_hidden_layers)
    ]
    # The released model uses multimodal RoPE. These sections sum to head_dim / 2.
    text.rope_parameters = {
        "rope_type": "default",
        "rope_theta": 10_000.0,
        "partial_rotary_factor": 1.0,
        "mrope_interleaved": True,
        "mrope_section": [11, 11, (model.head_dim // 2) - 22],
    }
    config.text_config = text
    config._attn_implementation = attention_backend
    return config


def _causal_forward(
    self,
    input_ids=None,
    attention_mask=None,
    position_ids=None,
    past_key_values=None,
    inputs_embeds=None,
    labels=None,
    use_cache=None,
    cache_position=None,
    logits_to_keep=0,
    **kwargs,
):
    """Compatibility forward missing from upstream's released CausalLM class."""
    from transformers.modeling_outputs import CausalLMOutputWithPast

    num_items_in_batch = kwargs.pop("num_items_in_batch", None)
    outputs = self.model(
        input_ids=input_ids,
        attention_mask=attention_mask,
        position_ids=position_ids,
        past_key_values=past_key_values,
        inputs_embeds=inputs_embeds,
        use_cache=use_cache,
        cache_position=cache_position,
        **kwargs,
    )
    hidden_states = outputs.last_hidden_state
    if labels is None and isinstance(logits_to_keep, int) and logits_to_keep > 0:
        hidden_states = hidden_states[:, -logits_to_keep:, :]
    logits = self.lm_head(hidden_states)

    loss = None
    if labels is not None:
        loss = self.loss_function(
            logits=logits,
            labels=labels,
            vocab_size=self.config.vocab_size,
            num_items_in_batch=num_items_in_batch,
        )
        router_logits = getattr(outputs, "router_logits", None)
        if router_logits:
            upstream = sys.modules[self.__class__.__module__]
            auxiliary_loss = upstream.load_balancing_loss_func(
                router_logits,
                self.num_experts,
                self.num_experts_per_tok,
                attention_mask,
            )
            loss = loss + self.router_aux_loss_coef * auxiliary_loss

    return CausalLMOutputWithPast(
        loss=loss,
        logits=logits,
        past_key_values=getattr(outputs, "past_key_values", None),
        hidden_states=getattr(outputs, "hidden_states", None),
        attentions=getattr(outputs, "attentions", None),
    )


def _install_upstream_forward_adapter(model):
    # Upstream revision 1b23c97 exposes AutoModelForCausalLM without forward().
    # Keep this adapter until the official remote implementation supplies it.
    from transformers.masking_utils import create_sliding_window_causal_mask

    upstream = sys.modules[model.__class__.__module__]
    # The released text model hard-codes create_causal_mask. Replacing that
    # imported symbol activates Transformers' native sliding-window mask.
    upstream.create_causal_mask = create_sliding_window_causal_mask
    model.__class__.forward = _causal_forward
    return model


def build_model(tokenizer, model: ModelConfig, data: DataConfig):
    from transformers import AutoConfig, AutoModelForCausalLM

    attention_backend = resolve_attention_backend(model.attention_backend)
    config = AutoConfig.from_pretrained(
        model.architecture_repo,
        revision=model.architecture_revision,
        code_revision=model.architecture_revision,
        trust_remote_code=True,
    )
    config = configure_model(config, tokenizer, model, data, attention_backend)
    model_instance = AutoModelForCausalLM.from_config(
        config,
        trust_remote_code=True,
        code_revision=model.architecture_revision,
        attn_implementation=attention_backend,
    )
    model_instance = _install_upstream_forward_adapter(model_instance)
    model_instance.config.name_or_path = model.name
    return model_instance


def load_trained_model(tokenizer, checkpoint_dir, model: ModelConfig, data: DataConfig):
    """Rebuild the pinned architecture and load Trainer's safetensors checkpoint."""
    from safetensors.torch import load_file

    model_instance = build_model(tokenizer, model, data)
    checkpoint = Path(checkpoint_dir) / "model.safetensors"
    if not checkpoint.exists():
        raise FileNotFoundError("Expected Trainer checkpoint at {}".format(checkpoint))
    missing, unexpected = model_instance.load_state_dict(
        load_file(str(checkpoint), device="cpu"),
        strict=False,
    )
    if set(missing) - {"lm_head.weight"} or unexpected:
        raise RuntimeError("Checkpoint mismatch: missing={}, unexpected={}".format(missing, unexpected))
    model_instance.tie_weights()
    return model_instance
