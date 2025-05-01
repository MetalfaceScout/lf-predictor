#!/usr/bin/env python3


################################################################
#
# These custom classes help with pipeline building and debugging
#
import sklearn.base

class PipelineNoop(sklearn.base.BaseEstimator, sklearn.base.TransformerMixin):
    """
    Just a placeholder with no actions on the data.
    """
    
    def __init__(self):
        return

    def fit(self, X, y=None):
        self.is_fitted_ = True
        return self

    def transform(self, X, y=None):
        return X

class Printer(sklearn.base.BaseEstimator, sklearn.base.TransformerMixin):
    """
    Pipeline member to display the data at this stage of the transformation.
    """
    
    def __init__(self, title):
        self.title = title
        return

    def fit(self, X, y=None):
        self.is_fitted_ = True
        return self

    def transform(self, X, y=None):
        print("{}::type(X)".format(self.title), type(X))
        print("{}::X.shape".format(self.title), X.shape)
        if not isinstance(X, pd.DataFrame):
            print("{}::X[0]".format(self.title), X[0])
        print("{}::X".format(self.title), X)
        return X

class DataFrameSelector(sklearn.base.BaseEstimator, sklearn.base.TransformerMixin):
    
    def __init__(self, do_predictors=True, do_numerical=True):
        #Age,Gender,,,,,,,,,,,
        self.mCategoricalPredictors = []
        self.mNumericalPredictors = ["green_commander_score", "green_commander_mvp", "green_commander_acc", "green_commander_hit_diff", "green_commander_missiles", "green_commander_medic_hits","green_heavy_score", "green_heavy_mvp", "green_heavy_avg_acc", "green_heavy_hit_diff", "green_heavy_missiles", "green_heavy_medic_hits", "green_scout_score", "green_scout_mvp", "green_scout_acc", "green_scout_hit_diff", "green_scout_3hit", "green_scout_medic_hits", "green_scout_rapid_fire", "green_scout2_score", "green_scout2_mvp", "green_scout2_acc", "green_scout2_hit_diff", "green_scout2_3hit", "green_scout2_medic_hits", "green_scout2_rapid_fire","green_ammo_score", "green_ammo_mvp", "green_ammo_acc", "green_ammo_hit_diff", "green_ammo_boosts", "green_ammo_resups","green_medic_score", "green_medic_mvp", "green_medic_acc", "green_medic_hit_diff", "green_medic_boosts", "green_medic_resups", "green_medic_lives_left", "green_medic_elim_rate","red_commander_score", "red_commander_mvp", "red_commander_acc", "red_commander_hit_diff", "red_commander_missiles", "red_commander_medic_hits","red_heavy_score", "red_heavy_mvp", "red_heavy_avg_acc", "red_heavy_hit_diff", "red_heavy_missiles", "red_heavy_medic_hits","red_scout_score", "red_scout_mvp", "red_scout_acc", "red_scout_hit_diff", "red_scout_3hit", "red_scout_medic_hits", "red_scout_rapid_fire","red_scout2_score", "red_scout2_mvp", "red_scout2_acc", "red_scout2_hit_diff", "red_scout2_3hit", "red_scout2_medic_hits", "red_scout2_rapid_fire","red_ammo_score", "red_ammo_mvp", "red_ammo_acc", "red_ammo_hit_diff", "red_ammo_boosts", "red_ammo_resups","red_medic_score", "red_medic_mvp", "red_medic_acc", "red_medic_hit_diff", "red_medic_boosts", "red_medic_resups", "red_medic_lives_left", "red_medic_elim_rate"]
        self.mLabels = ["winner"]
        self.do_numerical = do_numerical
        self.do_predictors = do_predictors
        
        if do_predictors:
            if do_numerical:
                self.mAttributes = self.mNumericalPredictors
            else:
                self.mAttributes = self.mCategoricalPredictors                
        else:
            self.mAttributes = self.mLabels
            
        return

    def fit( self, X, y=None ):
        # no fit necessary
        self.is_fitted_ = True
        return self

    def transform( self, X, y=None ):
        # only keep columns selected
        values = X[self.mAttributes]
        return values

#
# These custom classes help with pipeline building and debugging
#
################################################################
