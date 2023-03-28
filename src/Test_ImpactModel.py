import unittest
import numpy as np
from ImpactModel import ImpactModel

class Test_ImpactModel(unittest.TestCase):

    def setUp(self):
        # Initialize variables to be used in the tests
        self.vol = np.abs(np.random.normal(0,1,100000))  # Absolute values of random normal distribution
        self.x_v = np.random.normal(0, 1, 100000)  # Random normal distribution
        self.beta = 0.5  # True value of beta parameter
        self.eta =1.5  # True value of eta parameter
        # Generate the response variable h based on the true values of beta and eta, 
        # and add some noise using a normal distribution
        self.h = self.vol*self.eta*(np.abs(self.x_v)**self.beta)*np.sign(self.x_v) + np.random.normal(0,0.01,100000)
        self.imm = ImpactModel(window=10)  # Create an instance of ImpactModel class

    def test_nls(self):
        delta = 1e-2  # Tolerance level for comparing estimated and true values
        # Estimate the values of eta and beta using the NLS regression method
        results = self.imm.nls(self.vol,self.x_v,self.h)
        # Check whether the estimated values of eta and beta are close enough to the true values with a given tolerance delta
        self.assertAlmostEqual(results.x[0],self.eta,None,None,delta*self.eta)
        self.assertAlmostEqual(results.x[1],self.beta,None,None,delta*self.beta)
    
    def test_paired_bootstrap(self):
        delta = 1e-2  # Tolerance level for comparing estimated and true values
        # Perform paired bootstrap to estimate standard errors and p-values of eta and beta
        eta,beta,_,_,p_eta,p_beta = self.imm.paired(self.vol,self.x_v,self.h, num_iter=10)
        # Check whether the estimated values of eta, beta, p_eta, and p_beta are close enough to the true values with a given tolerance delta
        self.assertAlmostEqual(eta,self.eta,None,None,delta*self.eta)
        self.assertAlmostEqual(beta,self.beta,None,None,delta*self.beta)
        self.assertAlmostEqual(p_eta,0,None,None,delta)
        self.assertAlmostEqual(p_beta,0,None,None,delta)
    
    def test_residual_bootstrap(self):
        delta = 1e-2  # Tolerance level for comparing estimated and true values
        # Perform residual bootstrap to estimate standard errors and p-values of eta and beta
        eta,beta,_,_,p_eta,p_beta = self.imm.residual(self.vol,self.x_v,self.h, num_iter=10)
        # Check whether the estimated values of eta, beta, p_eta, and p_beta are close enough to the true values with a given tolerance delta
        self.assertAlmostEqual(eta,self.eta,None,None,delta*self.eta)
        self.assertAlmostEqual(beta,self.beta,None,None,delta*self.beta)
        self.assertAlmostEqual(p_eta,0,None,None,delta)
        self.assertAlmostEqual(p_beta,0,None,None,delta)
    
    def test_whites(self):
        # Estimate the parameters of the NLS regression
        params = self.imm.nls(self.vol,self.x_v,self.h).x
        # Get the residuals from the NLS regression
        resid = self.imm.getResid(params,self.x_v,self.vol,self.h)
        # Test whether the residuals are homoskedastic using the Whites test, and check whether the p-value is greater than 0.05
        p_value = self.imm.homoskedasticTest(resid,self.x_v,self.vol)
        self.assertGreater(p_value,0.05)

