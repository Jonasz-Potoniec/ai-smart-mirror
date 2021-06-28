from argparse import ArgumentParser

from pytorch_lightning import LightningModule
from pytorch_lightning.metrics import Recall
from torch.nn.functional import binary_cross_entropy
from torch.optim import Adam


class MaskClassifier(LightningModule):
    # TODO: add docstrings
    def __init__(self, net, learning_rate=0.001):
        super().__init__()
        self.net = net
        self.learning_rate = learning_rate
        self.recall = Recall()

    def forward(self, x):
        # TODO: add docstrings
        return self.net(x)

    # TODO: resolve lack of usage of batch_idx
    def training_step(self, batch, batch_idx):
        # TODO: add docstrings
        x, y = batch
        out = self.net(x)
        loss = binary_cross_entropy(out, y)
        recall = self.recall(out, y)

        self.log('train_loss', loss, on_step=False, on_epoch=True)
        self.log('train_recall', recall, on_step=False, on_epoch=True)

        return loss

    # TODO: resolve lack of usage of batch_idx
    def validation_step(self, batch, batch_idx):
        # TODO: add docstrings
        x, y = batch
        out = self.net(x)
        loss = binary_cross_entropy(out, y)
        recall = self.recall(out, y)

        self.log('val_loss', loss, on_step=False, on_epoch=True)
        self.log('val_recall', recall, on_step=False, on_epoch=True)

        return loss

    # TODO: resolve lack of usage of batch_idx
    def test_step(self, batch, batch_idx):
        # TODO: add docstrings
        x, y = batch
        out = self.net(x)
        loss = binary_cross_entropy(out, y)
        recall = self.recall(out, y)

        self.log('test_loss', loss, on_step=False, on_epoch=True)
        self.log('test_recall', recall, on_step=False, on_epoch=True)

        return loss

    def configure_optimizers(self):
        # TODO: add docstrings
        return Adam(self.parameters(), lr=self.learning_rate)

    @staticmethod
    def add_model_specific_args(parent_parser):
        # TODO: add docstrings
        parser = ArgumentParser(parents=[parent_parser], add_help=False)
        parser.add_argument('--learning_rate', type=float, default=0.001)
        return parser