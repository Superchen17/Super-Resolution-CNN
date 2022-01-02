from torch import nn
import torch.nn.functional as F

class SRCNN(nn.Module):
    def __init__(self):
        super(SRCNN, self).__init__()

        self.conv1 = nn.Conv2d(in_channels=1, out_channels=64, kernel_size=9, padding=2, padding_mode='replicate')
        self.conv2 = nn.Conv2d(in_channels=64, out_channels=32, kernel_size=1, padding=2, padding_mode='replicate')
        self.conv3 = nn.Conv2d(in_channels=32, out_channels=1, kernel_size=5, padding=2, padding_mode='replicate')

    def forward(self, x):
        '''feed foward algorithm
        
        '''
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = self.conv3(x)
        return x

if __name__ == "__main__":
    srcnn = SRCNN()
    print(srcnn.eval())
    