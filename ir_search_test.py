from ir_search import IRSearchManager

def main():

    app = IRSearchManager()

    # Example query
    query = "Compare list of Food insecurity reason in 2023 and 2024?"
    results = app.query_documents(query)

    # Print results
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Content: {result['content']}...")
        print(f"Source: {result['metadata']['source']}")
        print(f"Relevance Score: {result['relevance_score']}")

if __name__ == "__main__":
    main()