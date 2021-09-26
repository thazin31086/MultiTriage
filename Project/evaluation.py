def c_f1_macro(y_true, y_pred):
    """Computes 3 different f1 scores, micro macro
    weighted.
    micro: f1 score accross the classes, as 1
    macro: mean of f1 scores per class
    weighted: weighted average of f1 scores per class,
            weighted from the support of each class


    Args:
        y_true (Tensor): labels, with shape (batch, num_classes)
        y_pred (Tensor): model's predictions, same shape as y_true

    Returns:
        tuple(Tensor): (micro, macro, weighted)
                    tuple of the computed f1 scores
    """

    f1s = [0, 0, 0]

    y_true = tf.cast(y_true, tf.float64)
    y_pred = tf.cast(y_pred, tf.float64)

    for i, axis in enumerate([None, 0]):
        TP = tf.math.count_nonzero(y_pred * y_true, axis=axis)
        FP = tf.math.count_nonzero(y_pred * (y_true - 1), axis=axis)
        FN = tf.math.count_nonzero((y_pred - 1) * y_true, axis=axis)

        precision = TP / (TP + FP)
        recall = TP / (TP + FN)
        f1 = 2 * precision * recall / (precision + recall)

        f1s[i] = tf.reduce_mean(f1)

    weights = tf.reduce_sum(y_true, axis=0)
    weights /= tf.reduce_sum(weights)

    f1s[2] = tf.reduce_sum(f1 * weights)

    micro, macro, weighted = f1s
    return macro

def hammingloss(y_true, y_pred, threshold = 0.5, mode = 'multilabel'):
    """Computes hamming loss.
    Hamming loss is the fraction of wrong labels to the total number
    of labels.
    In multi-class classification, hamming loss is calculated as the
    hamming distance between `actual` and `predictions`.
    In multi-label classification, hamming loss penalizes only the
    individual labels.
    Args:
        y_true: actual target value
        y_pred: predicted target value
        threshold: Elements of `y_pred` greater than threshold are
            converted to be 1, and the rest 0. If threshold is
            None, the argmax is converted to 1, and the rest 0.
        mode: multi-class or multi-label
    Returns:
        hamming loss: float
    Usage:
    ```python
    # multi-class hamming loss
    hl = HammingLoss(mode='multiclass', threshold=0.6)
    actuals = tf.constant([[1, 0, 0, 0],[0, 0, 1, 0],
                       [0, 0, 0, 1],[0, 1, 0, 0]],
                      dtype=tf.float32)
    predictions = tf.constant([[0.8, 0.1, 0.1, 0],
                               [0.2, 0, 0.8, 0],
                               [0.05, 0.05, 0.1, 0.8],
                               [1, 0, 0, 0]],
                          dtype=tf.float32)
    hl.update_state(actuals, predictions)
    print('Hamming loss: ', hl.result().numpy()) # 0.25
    # multi-label hamming loss
    hl = HammingLoss(mode='multilabel', threshold=0.8)
    actuals = tf.constant([[1, 0, 1, 0],[0, 1, 0, 1],
                       [0, 0, 0,1]], dtype=tf.int32)
    predictions = tf.constant([[0.82, 0.5, 0.90, 0],
                               [0, 1, 0.4, 0.98],
                               [0.89, 0.79, 0, 0.3]],
                               dtype=tf.float32)
    hl.update_state(actuals, predictions)
    print('Hamming loss: ', hl.result().numpy()) # 0.16666667
    ```
    """
    if mode not in ["multiclass", "multilabel"]:
        raise TypeError("mode must be either multiclass or multilabel]")

    if threshold is None:
        threshold = tf.reduce_max(y_pred, axis=-1, keepdims=True)
        # make sure [0, 0, 0] doesn't become [1, 1, 1]
        # Use abs(x) > eps, instead of x != 0 to check for zero
        y_pred = tf.logical_and(y_pred >= threshold, tf.abs(y_pred) > 1e-12)
    else:
        y_pred = y_pred > threshold

    y_true = tf.cast(y_true, tf.int32)
    y_pred = tf.cast(y_pred, tf.int32)

    if mode == "multiclass":
        nonzero = tf.cast(tf.math.count_nonzero(y_true * y_pred, axis=-1), tf.float32)
        return 1.0 - nonzero

    else:
        nonzero = tf.cast(tf.math.count_nonzero(y_true - y_pred, axis=-1), tf.float32)
        return nonzero / y_true.get_shape()[-1]

def c_precision(y_true, y_pred):
    '''Calculates the precision, a metric for multi-label classification of
    how many selected items are relevant.
    '''
    y_pred = tf.cast(y_pred, tf.float32)
    y_true = tf.cast(y_true, tf.float32)
    true_positives = tf.cast(K.sum(K.round(K.clip(y_true * y_pred, 0, 1))), tf.float32)
    predicted_positives = tf.cast(K.sum(K.round(K.clip(y_pred, 0, 1))), tf.float32)
    precision = tf.cast(true_positives / (predicted_positives + K.epsilon()), tf.float32)
    return precision

def c_recall(y_true, y_pred):
    y_pred = tf.cast(y_pred, tf.float32)
    y_true = tf.cast(y_true, tf.float32)
    '''Calculates the recall, a metric for multi-label classification of
    how many relevant items are selected.
    '''
    true_positives = tf.cast(K.sum(K.round(K.clip(y_true * y_pred, 0, 1))), tf.float32)
    possible_positives = tf.cast(K.sum(K.round(K.clip(y_true, 0, 1))), tf.float32)
    recall = tf.cast(true_positives / (possible_positives + K.epsilon()), tf.float32)
    return recall
    
def c_fbeta(y_true, y_pred, beta=2):
    y_pred = backend.clip(y_pred, 0, 1)
    # calculate elements
    tp = backend.sum(backend.round(backend.clip(y_true * y_pred, 0, 1)), axis=1)
    fp = backend.sum(backend.round(backend.clip(y_pred - y_true, 0, 1)), axis=1)
    fn = backend.sum(backend.round(backend.clip(y_true - y_pred, 0, 1)), axis=1)
    # calculate precision
    p = tp / (tp + fp + backend.epsilon())
    # calculate recall
    r = tp / (tp + fn + backend.epsilon())
    # calculate fbeta, averaged across each class
    bb = beta ** 2
    fbeta_score = backend.mean((1 + bb) * (p * r) / (bb * p + r + backend.epsilon()))
    return fbeta_score

def c_auroc(y_true, y_pred):
    y_pred = tf.cast(y_pred, tf.float32)
    y_true = tf.cast(y_true, tf.float32)
    auc = tf.cast(tf.metrics.auc(y_true, y_pred)[1], tf.float32)
    K.get_session().run(tf.local_variables_initializer())
    return auc
