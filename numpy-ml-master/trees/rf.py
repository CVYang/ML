import numpy as np
from dt import DecisionTree


def bootstrap_sample(X, Y):
    N, M = X.shape
    idxs = np.random.choice(N, N, replace=True)
    return X[idxs], Y[idxs]


class RandomForest:
    """
    A random forest of decision trees.
    """

    def __init__(
        self, n_trees, max_depth, n_feats, classifier=True, criterion="entropy"
    ):
        """
        An ensemble (forest) of decision trees where each split is calculated
        using a random subset of the features in the input.

        Parameters
        ----------
        n_trees : int
            The number of individual decision trees to use within the ensemble.
        max_depth: int or None
            The depth at which to stop growing each decision tree. If `None`,
            grow each tree until the leaf nodes are pure.
        n_feats : int
            The number of features to sample on each split.
        criterion : str (default: 'entropy')
            The error criterion to use when calculating splits. Valid entries
            are {'entropy', 'gini'}.
        """
        self.trees = []
        self.n_trees = n_trees
        self.n_feats = n_feats
        self.max_depth = max_depth
        self.criterion = criterion
        self.classifier = classifier

    def fit(self, X, Y):
        """
        Create `n_trees`-worth of bootstrapped samples from the training data
        and use each to fit a separate decision tree.
        """
        self.trees = []
        for _ in range(self.n_trees):
            X_samp, Y_samp = bootstrap_sample(X, Y)
            tree = DecisionTree(
                n_feats=self.n_feats,
                max_depth=self.max_depth,
                criterion=self.criterion,
                classifier=self.classifier,
            )
            tree.fit(X_samp, Y_samp)
            self.trees.append(tree)

    def predict(self, X):
        """
        Predict the target value for each entry in X.

        Parameters
        ----------
        X : numpy array of shape (N, M)
            The training data of N examples, each with M features

        Returns
        -------
        y_pred : np.array of shape (N,)
            Model predictions for each entry in X.
        """
        tree_preds = np.array([[t._traverse(x, t.root) for x in X] for t in self.trees])
        return self._vote(tree_preds)

    def _vote(self, predictions):
        """
        Return the aggregated prediction across all trees in the RF for each problem.

        Parameters
        ----------
        predictions : np.array of shape (n_trees, N)
            The array of predictions from each decision tree in the RF for each
            of the N problems in X

        Returns
        -------
        y_pred : np.array of shape (N,)
            If classifier is True, the class label predicted by the majority of
            the decision trees for each problem in X. If classifier is False,
            the average prediction across decision trees on each problem.
        """
        if self.classifier:
            out = [np.bincount(x).argmax() for x in predictions.T]
        else:
            out = [np.mean(x) for x in predictions.T]
        return np.array(out)
