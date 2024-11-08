import weave
import pandas as pd


def get_evaluation_predictions(
    weave_client: weave.trace.weave_client.WeaveClient, 
    eval_call_id: str
) -> pd.DataFrame:
    """
    Retrieves evaluation predictions from a Weave call and returns them as a DataFrame.

    Args:
        weave_client (weave.trace.weave_client.WeaveClient): W&B weave client
        eval_call_id (str): The ID of the Weave evaluation call to analyze

    Returns:
        pd.DataFrame: DataFrame containing the evaluation data with predictions
    """
    eval_calls = weave_client.get_call(eval_call_id)

    predictions = []
    for eval_call in eval_calls.children():
        if eval_call.op_name.split("/")[-1].split(":")[0] == "Evaluation.predict_and_score":
            _eval_call = weave_client.get_call(eval_call.id)
            data = dict(_eval_call.inputs["example"])
            data.update({"pred_score": dict(_eval_call.output)["output"]["score"]})
            predictions.append(data)

    return pd.DataFrame(predictions)


def calculate_cohen_kappa(df: pd.DataFrame, labels: list) -> float:
    """
    Calculate Cohen's Kappa score between human scores and model predictions.

    Args:
        df (pd.DataFrame): DataFrame containing 'score' and 'pred_score' columns
        labels (list): List of label values to consider in the calculation

    Returns:
        float: Cohen's Kappa score with linear weights

    Raises:
        AssertionError: If required columns 'score' or 'pred_score' are missing from DataFrame
    """
    required_cols = ['score', 'pred_score']
    missing_cols = [col for col in required_cols if col not in df.columns]

    assert len(missing_cols) == 0, (
        f"DataFrame is missing required columns: {missing_cols}. "
        f"Please ensure DataFrame contains both 'score' and 'pred_score' columns."
    )

    if isinstance(df["pred_score"][0], str):
        score = df['score'].apply(lambda x: 'Bad' if 1 <= x <= 3 else 'Excellent')
        labels = ['Bad', 'Excellent']
    else:
        score = df["score"]

    from sklearn.metrics import cohen_kappa_score
    return cohen_kappa_score(
        score,
        df['pred_score'],
        labels=labels,
        weights='linear'
    )


def calculate_kendall_tau(df: pd.DataFrame) -> float:
    """
    Calculate Cohen's Kappa score between human scores and model predictions.

    Args:
        df (pd.DataFrame): DataFrame containing 'score' and 'pred_score' columns
        labels (list): List of label values to consider in the calculation

    Returns:
        float: Cohen's Kappa score with linear weights

    Raises:
        AssertionError: If required columns 'score' or 'pred_score' are missing from DataFrame
    """
    required_cols = ['score', 'pred_score']
    missing_cols = [col for col in required_cols if col not in df.columns]

    assert len(missing_cols) == 0, (
        f"DataFrame is missing required columns: {missing_cols}. "
        f"Please ensure DataFrame contains both 'score' and 'pred_score' columns."
    )

    from scipy.stats import kendalltau
    return kendalltau(
        df["score"],
        df['pred_score']
    ).statistic
