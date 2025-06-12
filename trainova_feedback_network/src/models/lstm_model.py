class LSTMModel(nn.Module):
    """
    PyTorch LSTM model for weight prediction
    """
    def __init__(self, input_size=1, hidden_size=50, output_size=1):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.dropout = nn.Dropout(0.2)
        self.fc = nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        # x shape: (batch_size, seq_len, input_size)
        lstm_out, _ = self.lstm(x)
        # Take the output from the last time step
        lstm_out = lstm_out[:, -1, :]
        x = self.dropout(lstm_out)
        x = self.fc(x)
        return x