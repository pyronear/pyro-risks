import pyro_risks


__all__ = ['predictor']


predictor = pyro_risks.models.predict.PyroRisk(which='RF')
