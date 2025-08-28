# 학습 설정 (1.6단계)
hardware:
  cuda: true
  gpu_name: NVIDIA GeForce RTX 4080
common:
  seq_len_tokens: 1024
  precision: "amp_fp16"
  grad_clip: 1.0
  save_every_steps: 1000
  val_every_steps: 500
melody_transformer:
  layers: 6
  d_model: 256
  n_heads: 8
  ff_dim: 1024
  dropout: 0.1
  batch_size: 24
  grad_accum: 1
  lr: 3e-4
drum_vae:
  bars: 4
  steps_per_bar: 16
  drum_classes: 9
  latent_dim: 32
  hidden_dim: 256
  batch_size: 128
  grad_accum: 1
  lr: 1e-3
