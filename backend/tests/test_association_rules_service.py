import pandas as pd

from app.infrastructure.services.association_rules_service import (
    MlxtendAssociationRulesService,
)


def test_mine_rules_returns_rules_with_current_mlxtend_signature():
    data = pd.DataFrame(
        {
            "cor": ["A", "A", "A", "B"],
            "turno": ["Noite", "Noite", "Dia", "Dia"],
        }
    )

    result = MlxtendAssociationRulesService().mine_rules(
        data,
        ["cor", "turno"],
        min_support=0.25,
        min_confidence=0.5,
    )

    assert result["algorithm"] == "Apriori + Association Rules"
    assert result["rules_count"] > 0
    assert {"antecedents", "consequents", "support", "confidence", "lift"} <= result["rules"][0].keys()
