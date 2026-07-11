# Model adapters

Only adapters that load and pass a real smoke test may be registered in the public factory.

`RETFoundCFPAdapter` implements the official RETFound MAE ViT-L/16 CFP encoder protocol: 256 px
bicubic evaluation preprocessing, ImageNet normalization, position-embedding interpolation from
the 224 px pretraining checkpoint, global average pooling, and a 1024-dimensional embedding.
Authenticated weights must be supplied with an explicit local `checkpoint_path`.
