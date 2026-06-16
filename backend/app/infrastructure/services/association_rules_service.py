from typing import Any
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules
from app.infrastructure.services.preprocessing import DataFramePreprocessor


class MlxtendAssociationRulesService:
    def __init__(self):
        self.preprocessor = DataFramePreprocessor()

    def mine_rules(self, df: pd.DataFrame, columns: list[str], min_support: float, min_confidence: float) -> dict[str, Any]:
        selected = self.preprocessor.select_features(df, columns)
        transactions = []
        for _, row in selected.iterrows():
            transaction = [f"{column}={row[column]}" for column in selected.columns if pd.notna(row[column])]
            transactions.append(transaction)

        encoder = TransactionEncoder()
        encoded = encoder.fit(transactions).transform(transactions)
        df_trans = pd.DataFrame(encoded, columns=encoder.columns_)
        frequent = apriori(df_trans, min_support=min_support, use_colnames=True)
        if frequent.empty:
            return {
                "algorithm": "Apriori",
                "rows_used": int(len(selected)),
                "rules_count": 0,
                "rules": [],
                "message": "Nenhuma regra encontrada com os parâmetros informados.",
            }

        rules = association_rules(frequent, metric="confidence", min_threshold=min_confidence)
        rules = rules.sort_values(["lift", "confidence", "support"], ascending=False).head(50)
        output = []
        for _, rule in rules.iterrows():
            output.append({
                "antecedents": sorted(list(rule["antecedents"])),
                "consequents": sorted(list(rule["consequents"])),
                "support": float(rule["support"]),
                "confidence": float(rule["confidence"]),
                "lift": float(rule["lift"]),
            })
        return {
            "algorithm": "Apriori + Association Rules",
            "rows_used": int(len(selected)),
            "columns_used": list(selected.columns),
            "min_support": min_support,
            "min_confidence": min_confidence,
            "rules_count": len(output),
            "rules": output,
        }
