from pyro_risks.models.predict import PyroRisk


__all__ = ["predictor"]


predictor = PyroRisk(which="RF")
