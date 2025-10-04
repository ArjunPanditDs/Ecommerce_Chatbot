from appp import rule_based, ml_intent, semantic_faq, semantic_product

print("🤖 Welcome to the Ecommerce Chatbot. Type 'quit' to exit.")
while True:
    user = input("You: ")
    if user.lower() == "quit":
        break

    # 1. Rule-based layer
    rb = rule_based(user)
    if rb:
        print("Bot:", rb)
        continue

    # 2. ML intent prediction
    intent = ml_intent(user)
    if intent in ["order_status", "return_query", "cancel_order", "payment_query", "account_create", "greeting"]:
        print("Bot:", semantic_faq(user))
    else:
        # 3. Semantic product search
        print("Bot:", semantic_product(user))
