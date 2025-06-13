import marimo

__generated_with = "0.13.13-dev18"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd

    return mo, pd


@app.cell
def _(mo):
    # Create UI elements
    funding_widget = mo.ui.number(value=225000, label="Loan Amount ($)", step=0.01)
    payment_widget = mo.ui.number(value=8156.25, label="Payment Amount ($)", step=0.01)
    term_widget = mo.ui.number(value=32, label="Terms", step=1)
    frequency_widget = mo.ui.dropdown(
        options=["Monthly", "Weekly"], value="Monthly", label="Payment Frequency"
    )

    # Display UI elements
    mo.vstack(
        [
            mo.md("# APR/APY Calculator"),
            funding_widget,
            payment_widget,
            term_widget,
            frequency_widget,
        ]
    )
    return frequency_widget, funding_widget, payment_widget, term_widget


@app.function
# Compute periodic rate using Newton-Raphson
def compute_rate(principal, payment, periods, guess=0.01, tol=1e-6, max_iter=1000):
    rate = guess
    for _ in range(max_iter):
        pv = payment * (1 - (1 + rate) ** -periods) / rate
        derivative = (payment * ((1 + rate) ** -periods * (periods * rate + 1) - 1)) / (
            rate**2
        )
        new_rate = rate - (pv - principal) / derivative
        if abs(new_rate - rate) < tol:
            return new_rate
        rate = new_rate
    raise ValueError("Failed to converge")


@app.cell
def _(pd):
    # Main function with payment frequency handling
    def calculate_apy(funding_amount, payment, term, frequency):
        periods = term
        total_repayment = payment * periods
        try:
            if frequency == "Monthly":
                rate = compute_rate(funding_amount, payment, periods)
                apy = (1 + rate) ** 12 - 1
                apr = rate * 12
                monthly_cost = payment
            elif frequency == "Weekly":
                rate = compute_rate(funding_amount, payment, periods)
                apy = (1 + rate) ** 52 - 1
                apr = rate * 52
                monthly_cost = total_repayment / (term / (52 / 12))
            else:
                raise ValueError("Unsupported frequency")

            return {
                "dash": {
                    "Monthly Cost": f"${monthly_cost:,.2f}",
                    "Total Repayment": f"${total_repayment:,.2f}",
                    "APY (Annual Percentage Yield)": f"{apy:.2%}",
                    "APR": f"{apr:.2%}",
                },
                "details": {
                    "Total Interest Paid": f"${total_repayment - funding_amount:,.2f}",
                    "Premium": f"{-1 + (total_repayment / funding_amount):.2%}",
                    f"{frequency} Interest Rate": f"{rate:.4%}",
                },
            }
        except Exception as e:
            return pd.DataFrame({"Error": [str(e)]})

    return (calculate_apy,)


@app.cell
def _(
    calculate_apy,
    frequency_widget,
    funding_widget,
    mo,
    payment_widget,
    pd,
    term_widget,
):
    # Calculate APY based on UI inputs
    results = calculate_apy(
        funding_widget.value,
        payment_widget.value,
        term_widget.value,
        frequency_widget.value,
    )

    results_dashboard = mo.hstack(
        [mo.stat(label=k, value=v) for k, v in results["dash"].items()],
        justify="center",
        gap=2,
    )
    # results_dashboard
    other_details = pd.DataFrame.from_dict(
        results["details"], orient="index", columns=["Value"]
    )

    mo.vstack(
        [
            mo.md("## Results"),
            results_dashboard,
            mo.md("---"),
            mo.md("### Detailed Breakdown"),
            other_details,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
