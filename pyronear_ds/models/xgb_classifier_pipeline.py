from pandas import DataFrame
from xgboost import XGBClassifier


class XGBClassifierPipeline:
    def __init__(self, classifier: XGBClassifier):
        self.classifier = classifier

    def pipeline(self, data: DataFrame):
        scores, predictions = self.classifier.get_predictions_and_scores(data)
        return scores, predictions
