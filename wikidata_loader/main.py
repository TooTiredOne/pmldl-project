from qwikidata.sparql import return_sparql_query_results
import pandas as pd


class WDRelationQuery:
    def __init__(
            self,
            orig_name: str,
            arg1_types: list[str],
            arg2_types: list[str],
            wikidata_ids: list[str]
    ):
        self.orig_name = orig_name
        self.arg1_types = arg1_types
        self.arg2_types = arg2_types
        self.wikidata_ids = wikidata_ids
        self.accepted_languages = ['ru, en']
        self.accepted_languages_as_str = ", ".join(self.accepted_languages)

    def __make_query__(self, relation_id: str, limit: int) -> str:
        return f"""
        SELECT ?item1 ?item1Label ?item2 ?item2Label
        {{
            ?item1 wdt:{relation_id} ?item2 .
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{self.accepted_languages_as_str}". }}
        }} limit {limit}
        """

    def make_request(self, limit: int):
        query = self.__make_query__(self.wikidata_ids[0], limit)
        result = return_sparql_query_results(query)
        bindings = result['results']['bindings']
        bindings_filtered = set()
        for b in bindings:
            label1_dict = b['item1Label']
            label2_dict = b['item2Label']
            if 'xml:lang' in label1_dict and 'xml:lang' in label2_dict:
                bindings_filtered.add((label1_dict['value'], label2_dict['value']))

        return bindings_filtered


relations_mapping = pd.read_csv('../relations_mapping.csv')

queries = []
for _, row in relations_mapping[relations_mapping['Wikidata'].notnull()].iterrows():
    wikidata_relation_query = WDRelationQuery(
                                row['Type'],
                                row['Argument1'],
                                row['Argument2'],
                                row['Wikidata'].split('|')
                              )
    queries.append(wikidata_relation_query)


print(queries[1].make_request(100))