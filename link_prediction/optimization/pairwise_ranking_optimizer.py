import tqdm
import torch
import numpy as np
from torch import optim
from link_prediction.optimization.negative_sampling import CorruptionEngine
from link_prediction.regularization.regularizers import L2
from model import Model, BATCH_SIZE, LEARNING_RATE, EPOCHS, MARGIN, NEGATIVE_SAMPLES_RATIO, \
    REGULARIZER_WEIGHT
from optimizer import Optimizer


class PairwiseRankingOptimizer(Optimizer):
    """
        This optimizer relies on Pairwise Ranking loss, also called Margin-based loss.

    """

    def __init__(self,
                 model: Model,
                 hyperparameters: dict,
                 verbose: bool = True):
        """
            PairwiseRankingOpti mizer initializer.
            :param model: the model to train
            :param hyperparameters: a dict with the optimization hyperparameters. It must contain at least:
                    - BATCH SIZE
                    - LEARNING RATE
                    - DECAY
                    - LABEL SMOOTHING
                    - EPOCHS
            :param verbose:
        """

        Optimizer.__init__(self, model=model, hyperparameters=hyperparameters, verbose=verbose)

        self.batch_size = hyperparameters[BATCH_SIZE]
        self.learning_rate = hyperparameters[LEARNING_RATE]
        self.epochs = hyperparameters[EPOCHS]
        self.margin = hyperparameters[MARGIN]
        self.negative_samples_ratio = hyperparameters[NEGATIVE_SAMPLES_RATIO]
        self.regularizer_weight = hyperparameters[REGULARIZER_WEIGHT]

        self.corruption_engine = CorruptionEngine(self.dataset)
        self.loss = torch.nn.MarginRankingLoss(margin=self.margin, reduction="mean").cuda()

        self.optimizer = optim.Adam(params=self.model.parameters(), lr=self.learning_rate)  # we only support ADAM for PairwiseRankingOptimizer
        self.regularizer = L2(self.regularizer_weight)

    def train(self,
              train_samples: np.array,
              save_path: str = None,
              evaluate_every:int =-1,
              valid_samples:np.array = None):

        print("Training the " + self.model.name + " model...")

        training_samples = np.vstack((train_samples, self.dataset.invert_samples(train_samples)))

        self.model.cuda()

        for e in range(1, self.epochs+1):
            self.epoch(training_samples=training_samples, batch_size=self.batch_size)

            if evaluate_every > 0 and valid_samples is not None and e % evaluate_every == 0:
                self.model.eval()
                with torch.no_grad():
                    mrr, h1, h10 = self.evaluator.eval(samples=valid_samples, write_output=False)

                print("\tValidation Hits@1: %f" % h1)
                print("\tValidation Hits@10: %f" % h10)
                print("\tValidation Mean Reciprocal Rank': %f" % mrr)

                if save_path is not None:
                    print("\t saving model...")
                    torch.save(self.model.state_dict(), save_path)
                print("\t done.")

        if save_path is not None:
            print("\t saving model...")
            torch.save(self.model.state_dict(), save_path)
            print("\t done.")

    def epoch(self,
              batch_size: int,
              training_samples: np.array):

        np.random.shuffle(training_samples)
        self.model.train()

        with tqdm.tqdm(total=len(training_samples), unit='ex', disable=not self.verbose) as bar:
            bar.set_description(f'train loss')
            batch_start = 0

            while batch_start < len(training_samples):
                positive_batch, negative_batch = self.extract_batch(training_samples=training_samples,
                                                                    batch_start=batch_start,
                                                                    batch_size=batch_size)

                l = self.step_on_batch(positive_batch, negative_batch)
                batch_start+=batch_size
                bar.update(batch_size)
                bar.set_postfix(loss=str(round(l.item(), 6)))

            #if self.decay:
            #    self.scheduler.step()

    def extract_batch(self, training_samples, batch_start, batch_size):
        original_batch = training_samples[batch_start: min(batch_start+batch_size, len(training_samples))]
        positive_batch, negative_batch = self.corruption_engine.corrupt_samples(original_batch, self.negative_samples_ratio)

        return torch.from_numpy(positive_batch).cuda(), torch.from_numpy(negative_batch).cuda()


    def step_on_batch(self, positive_batch, negative_batch):

        self.optimizer.zero_grad()

        positive_scores, positive_factors = self.model.forward(positive_batch)
        negative_scores, negative_factors = self.model.forward(negative_batch)
        target = torch.tensor([-1], dtype=torch.float).cuda()

        l_fit = self.loss(positive_scores, negative_scores, target)
        l_reg = (self.regularizer.forward(positive_factors) + self.regularizer.forward(negative_factors))/2

        loss = l_fit + l_reg
        loss.backward()
        self.optimizer.step()

        return loss

class KelpiePairwiseRankingOptimizer(PairwiseRankingOptimizer):
    def __init__(self,
                 model:Model,
                 hyperparameters: dict,
                 verbose: bool = True):

        super(KelpiePairwiseRankingOptimizer, self).__init__(model=model,
                                                             hyperparameters=hyperparameters,
                                                             verbose=verbose)

        self.optimizer = optim.SGD(params=self.model.parameters(), lr=hyperparameters[LEARNING_RATE])

    # Override

    def epoch(self,
              batch_size: int,
              training_samples: np.array):

        np.random.shuffle(training_samples)
        self.model.train()

        with tqdm.tqdm(total=len(training_samples), unit='ex', disable=not self.verbose) as bar:
            bar.set_description(f'train loss')

            batch_start = 0

            while batch_start < len(training_samples):
                positive_batch, negative_batch = self.extract_batch(training_samples=training_samples,
                                                                    batch_start=batch_start,
                                                                    batch_size=batch_size)

                l = self.step_on_batch(positive_batch, negative_batch)

                # THIS IS THE ONE DIFFERENCE FROM THE ORIGINAL OPTIMIZER.
                # THIS IS EXTREMELY IMPORTANT BECAUSE THIS WILL PROPAGATE THE UPDATES IN THE KELPIE ENTITY EMBEDDING
                # TO THE MATRIX CONTAINING ALL THE EMBEDDINGS
                self.model.update_embeddings()


                batch_start+=batch_size
                bar.update(batch_size)
                bar.set_postfix(loss=str(round(l.item(), 6)))