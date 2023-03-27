import torch
import torch.nn as nn
from torch.nn import TransformerEncoder, TransformerEncoderLayer
import torch.optim as optim
import os
from decimal import Decimal
from typing import Optional, Tuple
from sklearn.model_selection import train_test_split

from apps.django_projects.predictions.constants import DEFAULT_SEQ_LEN
from apps.prediction.constants import ModelType
from apps.prediction.models.base import AbstractBaseModel
from apps.prediction import utils


class _NumberTransformer(nn.Module):
    def __init__(
        self,
        input_size,
        d_model,
        nhead,  # NOQA
        num_layers,
        output_size,
        dropout=0.5,
    ):
        super(_NumberTransformer, self).__init__()
        self.encoder_layer = TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dropout=dropout
        )
        self.transformer_encoder = TransformerEncoder(
            self.encoder_layer, num_layers=num_layers
        )
        self.linear = nn.Linear(d_model, output_size)
        self.input_size = input_size
        self.d_model = d_model

    def forward(self, src):
        src = src.reshape(1, -1, self.input_size)
        src = src.permute(1, 0, 2)
        src_key_padding_mask = torch.zeros(src.size(1), src.size(0)).bool()
        encoder_out = self.transformer_encoder(
            src, src_key_padding_mask=src_key_padding_mask
        )
        out = self.linear(encoder_out[-1, :, :])
        return out


class TransformerModel(AbstractBaseModel):
    """
    transformer model class
    not use directly. Use CoreModel instead
    """

    MODEL_EXTENSION = "pth"

    def __init__(self, *, seq_len: Optional[int] = DEFAULT_SEQ_LEN):
        super().__init__(model_type=ModelType.TRANSFORMER, seq_len=seq_len)
        input_size = self.seq_len
        d_model = self.seq_len
        nhead = 2  # NOQA
        num_layers = 2
        output_size = 1
        self.model = _NumberTransformer(
            input_size, d_model, nhead, num_layers, output_size
        )
        self._epochs = 500

    def _compile_model(self) -> any:
        ...

    def load_model(self, *, name: str) -> None:
        model_path = self._get_model_path(name=name)
        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"file not found'{model_path}'")
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()

    def train(
        self,
        *,
        home_bet_id: int,
        multipliers: list[Decimal],
        test_size: Optional[float] = 0.2,
        epochs: Optional[int] = None,
    ) -> Tuple[str, float]:
        data = utils.transform_multipliers_to_data(multipliers)
        X, y = self._split_data_to_train(data=data)  # NOQA
        X_train, X_test, y_train, y_test = train_test_split(  # NOQA
            X, y, test_size=test_size, random_state=42
        )
        batch_size = 16
        train_loss = []
        loss_fn = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        epochs = epochs or self._epochs
        for epoch in range(epochs):
            for i in range(0, len(X_train), batch_size):
                batch_X = torch.tensor(  # NOQA
                    X_train[i: i + batch_size]
                ).float()
                batch_y = torch.tensor(y_train[i: i + batch_size]).float()
                optimizer.zero_grad()
                y_pred = self.model(batch_X)  # NOQA
                loss = loss_fn(y_pred, batch_y)
                loss.backward()
                optimizer.step()
                train_loss.append(loss.item())
            print(f"Epoch: {epoch + 1}/{epochs}, Loss: {train_loss[-1]}")
        name, model_path = self._generate_model_path_to_save(
            home_bet_id=home_bet_id
        )
        torch.save(self.model.state_dict(), model_path)
        print("---------------------------------------------")
        print(f"--------MODEL: {name} ERROR: {train_loss[-1]}----------")
        print("---------------------------------------------")
        return name, train_loss[-1]

    def predict(self, *, data: list[int]) -> Decimal:
        with torch.no_grad():
            X_tensor = torch.from_numpy(data[-self.seq_len :]).float()  # NOQA
            y_pred = self.model(X_tensor)  # NOQA
            return y_pred.item()
