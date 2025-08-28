# sanity_check.py 파일의 내용

import torch
import pretty_midi
import numpy as np

print('Torch:', torch.__version__, 'CUDA:', torch.cuda.is_available())
print('PrettyMIDI:', pretty_midi.__version__)