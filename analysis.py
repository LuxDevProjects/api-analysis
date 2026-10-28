"""
Day 1 - API Data Analysis Using Python Structures
Squad Python Specialization - Data Science, AI & Analytics
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import requests

API_URL = "https://jsonplaceholder.typicode.com/users"


def get_customers(url: str = API_URL) -> list[dict]:
    """Fetch the customer list. Report failures clearly instead of crashing."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print(f"Error: the request to {url} timed out.")
    except requests.exceptions.ConnectionError:
        print("Error: could not connect. Check your internet connection.")
    except requests.exceptions.HTTPError as e:
        print(f"Error: the server returned a bad status code ({e.response.status_code}).")
    except requests.exceptions.RequestException as e:
        print(f"Error: the request failed: {e}")
    except ValueError:
        print("Error: the response was not valid JSON.")
    return []


def explore(record: dict, indent: int = 0) -> None:
    """Print every key in a (possibly nested) record with its type, indented by depth."""
    for key, value in record.items():
        print(f"{'  ' * indent}{key}: {type(value).__name__}")
        if isinstance(value, dict):
            explore(value, indent + 1)


def extract_attributes(customers: list[dict]) -> list[dict]:
    """Return one flat dict per customer with the attributes listed in the task."""
    return [
        {
            "customer_id": c["id"],
            "name": c["name"],
            "username": c["username"],
            "email": c["email"],
            "email_domain": c["email"].split(".")[-1],
            "phone": c["phone"],
            "city": c["address"]["city"],
            "zipcode": c["address"]["zipcode"],
            "latitude": float(c["address"]["geo"]["lat"]),
            "longitude": float(c["address"]["geo"]["lng"]),
            "company": c["company"]["name"],
            "website": c["website"],
        }
        for c in customers
    ]


def unique_cities(customers: list[dict]) -> set[str]:
    """Return the set of distinct cities."""
    return {c["address"]["city"] for c in customers}


def city_counts(customers: list[dict]) -> dict[str, int]:
    """Count customers per city using a loop and/or a dict comprehension (no Counter, no pandas)."""
    counts = {}
    for c in customers:
        city = c["address"]["city"]
        counts[city] = counts.get(city, 0) + 1
    return counts


def email_domain_counts(customers: list[dict]) -> dict[str, int]:
    """Count customers per email top-level domain (e.g. 'biz', 'tv')."""
    domains = [c["email"].split(".")[-1] for c in customers]
    return {d: domains.count(d) for d in set(domains)}


def to_dataframe(rows: list[dict]) -> pd.DataFrame:
    """Convert the flat customer rows into a DataFrame."""
    return pd.DataFrame(rows)


def plot_distribution(counts: dict[str, int], path: Path, 
                      title: str = "Customer Distribution", xlabel: str = "Category",) -> None:
    """Save a labelled chart of the distribution to path."""
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    labels = [label for label, _ in ordered]
    values = [value for _, value in ordered]

    path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(labels, values)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Number of customers")
    ax.set_yticks(range(0, max(values) + 1))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Fetch
    customers = get_customers()
    if not customers:
        raise SystemExit(1)

    # Explore one record
    print("Structure of one customer record:")
    explore(customers[0])
    print()

    # Extract flat attributes
    rows = extract_attributes(customers)

    # Unique cities
    cities = unique_cities(customers)
    print(f"{len(cities)} unique cities for {len(customers)} customers")

    # Counts with plain Python, sorted most to least common
    by_city = city_counts(customers)
    by_domain = email_domain_counts(customers)
    sort_key = lambda item: (-item[1], item[0])
    sorted_cities = sorted(by_city.items(), key=sort_key)
    sorted_domains = dict(sorted(by_domain.items(), key=sort_key))
    print("City counts:", dict(sorted_cities))
    print("Email domain counts:", sorted_domains)
    print()

    # DataFrame and cross-check against the hand-written counts
    df = to_dataframe(rows)
    print("DataFrame shape:", df.shape)
    print(df.dtypes)
    print("City counts match pandas:", df["city"].value_counts().to_dict() == by_city)
    print("Domain counts match pandas:", df["email_domain"].value_counts().to_dict() == by_domain)
    print()

    # Export CSVs
    df.to_csv(output_dir / "customers.csv", index=False)
    city_df = pd.DataFrame(sorted_cities, columns=["city", "customer_count"])
    city_df.to_csv(output_dir / "city_counts.csv", index=False)

    # Charts
    city_chart = output_dir / "customer_distribution.png"
    domain_chart = output_dir / "email_domain_distribution.png"
    plot_distribution(by_city, city_chart, "Customers by City", "City")
    plot_distribution(by_domain, domain_chart, "Customers by Email Domain", "Email domain (TLD)")

    # Findings summary
    top_city, top_count = sorted_cities[0]
    print("Customers retrieved :", len(customers))
    print("Unique cities       :", len(cities))
    print(f"Most common city    : {top_city} ({top_count})")
    print("Email domains       :", sorted_domains)
    print("Chart saved to      :", city_chart.as_posix())
    print("Second chart saved  :", domain_chart.as_posix())