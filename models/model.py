import torch 
import torch.nn as nn 
import torch.nn.functional as F
from models.embedding import TransformerEmbedding
from models.layer import gMLPBLOCK_CLS


class gMLP(nn.Module):
    def __init__(self,d_model,d_ffn,seq_len,num_layers):
        super(gMLP,self).__init__()
        self.model = nn.Sequential(*[gMLPBLOCK_CLS(d_model,d_ffn,seq_len) for _ in range(num_layers)])
        
    def forward(self,x):
        x = self.model(x)
        return x

class MaskedLanguageModelingHead(nn.Module):
    def __init__(self, vocab_size, model_dim):
        super(MaskedLanguageModelingHead,self).__init__()
        self.linear_layer = nn.Linear(model_dim, vocab_size)
        self.softmax = nn.LogSoftmax(dim=-1)
    
    def forward(self, encoder_output):
        # mask_position = [bs, tgt_size(15% of sent)]
        mlm_prediction = self.softmax(self.linear_layer(encoder_output)) # [bs,sl,vocab_size]
        
        return mlm_prediction

class gMLP_LanguageModel(gMLP):
    def __init__(self,vocab_size, d_model, d_ffn, seq_len, num_layers,output_logits=False):
        super().__init__(d_model,d_ffn,seq_len,num_layers)
        self.embed = TransformerEmbedding(vocab_size,d_model,seq_len,0.1)
        self.output_logits = output_logits
        self.to_logits = MaskedLanguageModelingHead(vocab_size,d_model)

    def forward(self,x):
        embedding = self.embed(x)
        embedding = embedding
        output = self.model(embedding)
        if self.output_logits:
            output = self.to_logits(output)

        return output
    

def build_model(num_tokens, d_model, d_ffn, seq_len, num_layers,output_logits=False):
    
    model = gMLP_LanguageModel(num_tokens,d_model,d_ffn,seq_len,num_layers,output_logits)

    return model
