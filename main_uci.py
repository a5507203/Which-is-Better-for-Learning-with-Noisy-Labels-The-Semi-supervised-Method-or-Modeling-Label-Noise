

import argparse
from random import seed
from mylib.utils import fix_seed
from mylib.data.data_loader import load_ucidata
import numpy as np
from run_dnl import run_dnl
import tools

from kmeans import run_kmeans
# --- parsing and configuration --- #
parser = argparse.ArgumentParser(
    description="PyTorch implementation of VAE")
parser.add_argument('--batch_size', type=int, default=16,
                    help='batch size for training (default: 128)')
parser.add_argument('--epochs', type=int, default=10,
                    help='number of epochs to train (default: 20)')
parser.add_argument('--z_dim', type=int, default=25,
                    help='dimension of hidden variable Z (default: 10)')
parser.add_argument('--num_hidden_layers', type=int, default=2,
                    help='num hidden_layers (default: 0)')
parser.add_argument('--flip_rate_fixed', type=float,
                    help='fixed flip rates.', default=0.4)
parser.add_argument('--train_frac', default=1.0, type=float,
                    help='training sample size fraction')
parser.add_argument('--noise_type', type=str, default='sym')
parser.add_argument('--trainval_split',  default=0.8, type=float,
                    help='training set ratio')
parser.add_argument('--seed', default=1, type=int,
                    help='seed for initializing training')
parser.add_argument('--dataset', default="krkp", type=str,
                    help='db')
parser.add_argument('--select_ratio', default=0, type=float,
                    help='confidence example selection ratio')
parser.add_argument('--pretrained', default=0, type=int,
                    help='using pretrained model or not')

arch_dict = {"FashionMNIST":"resnet18","cifar10":"resnet18","cifar100":"resnet34","mnist":"Lenet","balancescale":"NaiveNet","krkp":"NaiveNet","splice":"NaiveNet","yxguassian":"NaiveNet"}


def main():
    args = parser.parse_args()
    base_dir = "./"+args.dataset+"/"+args.noise_type+str(args.flip_rate_fixed)+"/"+str(args.seed)+"/"
    print(args)
    
    if args.seed is not None:
        fix_seed(args.seed)
    train_val_loader, train_loader, val_loader, est_loader, test_loader = load_ucidata(
        dataset = args.dataset,  
        noise_type = args.noise_type,
        random_state = args.seed, 
        batch_size = args.batch_size, 
        add_noise = True, 
        flip_rate_fixed = args.flip_rate_fixed, 
        trainval_split = args.trainval_split,
        train_frac = args.train_frac,
        augment=False
    )
    test_dataset = test_loader.dataset
    val_dataset = val_loader.dataset

    train_dataset = train_loader.dataset
    T_prime = run_kmeans(train_dataset.dataset)

    T_star_hat, acc = run_dnl(
        train_data=train_dataset, 
        val_data = val_dataset,
        test_data = test_dataset, 
        noise_type = args.noise_type, 
        noise_rate = args.flip_rate_fixed, 
        dataset = args.dataset, 
        n_epoch = args.epochs,
        num_classes = train_val_loader.dataset._get_num_classes(),
        device=0,
        arch=arch_dict[args.dataset]
    )

    print("Estimation: %f" % tools.error(T_prime,T_star_hat))

if __name__ == "__main__":
    main()