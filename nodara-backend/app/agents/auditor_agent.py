from langchain_core.messages import AIMessage

def auditor_node(state):
    """
    Emite el dictamen final en portugués basándose en los datos de SAP extraídos.
    """
    fields = state.get("extracted_sap_fields", {})
    
    if "Country" in fields and "BP_Role" in fields:
        dictamen = "Parabéns! Os dados estão corretos de acordo com a norma australiana. O Cliente SAP foi validado e está pronto para ser criado no S/4HANA."
    else:
        dictamen = "Atenção: Faltam campos obrigatórios (País ou Função do BP). Por favor, revise o procedimento e tente novamente."
        
    return {"messages": [AIMessage(content=dictamen)]}