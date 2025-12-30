"""Custom Lightning Module wrapper to support non-strict checkpoint loading."""

from rslearn.train.lightning_module import RslearnLightningModule


class NonStrictRslearnLightningModule(RslearnLightningModule):
    """Wrapper that disables strict checkpoint loading.

    This allows loading checkpoints that have missing or extra keys compared
    to the current model definition. Useful when the model architecture has
    evolved since the checkpoint was created.
    """

    # Set strict_loading to False at the class level
    strict_loading = False
