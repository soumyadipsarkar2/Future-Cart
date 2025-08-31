"""
Evaluation utilities for customer purchase prediction.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    roc_auc_score, precision_recall_curve, average_precision_score,
    precision_score, recall_score, f1_score, confusion_matrix,
    classification_report, roc_curve, precision_recall_curve
)
from sklearn.calibration import calibration_curve
import shap
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Comprehensive model evaluation class."""
    
    def __init__(self, y_true: np.ndarray, y_pred: np.ndarray, y_proba: np.ndarray):
        """
        Initialize evaluator.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Predicted probabilities
        """
        self.y_true = y_true
        self.y_pred = y_pred
        self.y_proba = y_proba
        self.metrics = {}
        
    def calculate_basic_metrics(self) -> Dict[str, float]:
        """
        Calculate basic classification metrics.
        
        Returns:
            Dictionary of metrics
        """
        logger.info("Calculating basic metrics...")
        
        self.metrics = {
            'accuracy': (self.y_true == self.y_pred).mean(),
            'precision': precision_score(self.y_true, self.y_pred),
            'recall': recall_score(self.y_true, self.y_pred),
            'f1_score': f1_score(self.y_true, self.y_pred),
            'roc_auc': roc_auc_score(self.y_true, self.y_proba),
            'pr_auc': average_precision_score(self.y_true, self.y_proba)
        }
        
        logger.info(f"Basic metrics calculated: {self.metrics}")
        return self.metrics
    
    def calculate_precision_at_k(self, k_values: List[int] = None) -> Dict[int, float]:
        """
        Calculate precision at different k values.
        
        Args:
            k_values: List of k values to calculate precision for
            
        Returns:
            Dictionary of precision at k
        """
        if k_values is None:
            k_values = [10, 20, 50, 100]
            
        precision_at_k = {}
        
        # Sort by probability
        sorted_indices = np.argsort(self.y_proba)[::-1]
        sorted_true = self.y_true[sorted_indices]
        
        for k in k_values:
            if k <= len(sorted_true):
                precision_at_k[k] = sorted_true[:k].mean()
            else:
                precision_at_k[k] = sorted_true.mean()
                
        return precision_at_k
    
    def calculate_recall_at_k(self, k_values: List[int] = None) -> Dict[int, float]:
        """
        Calculate recall at different k values.
        
        Args:
            k_values: List of k values to calculate recall for
            
        Returns:
            Dictionary of recall at k
        """
        if k_values is None:
            k_values = [10, 20, 50, 100]
            
        recall_at_k = {}
        total_positive = self.y_true.sum()
        
        # Sort by probability
        sorted_indices = np.argsort(self.y_proba)[::-1]
        sorted_true = self.y_true[sorted_indices]
        
        for k in k_values:
            if k <= len(sorted_true):
                recall_at_k[k] = sorted_true[:k].sum() / total_positive
            else:
                recall_at_k[k] = 1.0
                
        return recall_at_k
    
    def calculate_lift(self, deciles: int = 10) -> pd.DataFrame:
        """
        Calculate lift by deciles.
        
        Args:
            deciles: Number of deciles
            
        Returns:
            DataFrame with lift information
        """
        # Create deciles
        df = pd.DataFrame({
            'y_true': self.y_true,
            'y_proba': self.y_proba
        })
        
        df['decile'] = pd.qcut(df['y_proba'], deciles, labels=False, duplicates='drop')
        
        # Calculate lift
        lift_data = df.groupby('decile').agg({
            'y_true': ['count', 'sum', 'mean']
        }).reset_index()
        
        lift_data.columns = ['decile', 'count', 'positive_count', 'response_rate']
        lift_data['decile'] = lift_data['decile'] + 1
        
        # Calculate overall response rate
        overall_response_rate = self.y_true.mean()
        lift_data['lift'] = lift_data['response_rate'] / overall_response_rate
        
        # Calculate cumulative metrics
        lift_data['cumulative_count'] = lift_data['count'].cumsum()
        lift_data['cumulative_positive'] = lift_data['positive_count'].cumsum()
        lift_data['cumulative_response_rate'] = lift_data['cumulative_positive'] / lift_data['cumulative_count']
        lift_data['cumulative_lift'] = lift_data['cumulative_response_rate'] / overall_response_rate
        
        return lift_data
    
    def calculate_business_metrics(self, customer_values: np.ndarray = None,
                                 marketing_cost: float = 10.0,
                                 conversion_value: float = 100.0) -> Dict[str, float]:
        """
        Calculate business metrics.
        
        Args:
            customer_values: Customer lifetime values
            marketing_cost: Cost per marketing contact
            conversion_value: Value of successful conversion
            
        Returns:
            Dictionary of business metrics
        """
        logger.info("Calculating business metrics...")
        
        # Sort by probability
        sorted_indices = np.argsort(self.y_proba)[::-1]
        sorted_true = self.y_true[sorted_indices]
        
        business_metrics = {}
        
        # Calculate ROI for different targeting strategies
        for k in [100, 500, 1000]:
            if k <= len(sorted_true):
                # Marketing cost
                total_cost = k * marketing_cost
                
                # Expected conversions
                expected_conversions = sorted_true[:k].sum()
                expected_revenue = expected_conversions * conversion_value
                
                # ROI
                roi = (expected_revenue - total_cost) / total_cost
                net_profit = expected_revenue - total_cost
                
                business_metrics[f'roi_at_{k}'] = roi
                business_metrics[f'net_profit_at_{k}'] = net_profit
                business_metrics[f'expected_conversions_at_{k}'] = expected_conversions
        
        # Calculate expected value
        if customer_values is not None:
            sorted_values = customer_values[sorted_indices]
            expected_value = (sorted_true * sorted_values).sum()
            business_metrics['expected_value'] = expected_value
        
        return business_metrics
    
    def plot_roc_curve(self, save_path: str = None) -> None:
        """
        Plot ROC curve.
        
        Args:
            save_path: Path to save the plot
        """
        fpr, tpr, _ = roc_curve(self.y_true, self.y_proba)
        auc = roc_auc_score(self.y_true, self.y_proba)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {auc:.3f})')
        plt.plot([0, 1], [0, 1], 'k--', label='Random')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curve')
        plt.legend()
        plt.grid(True)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_precision_recall_curve(self, save_path: str = None) -> None:
        """
        Plot Precision-Recall curve.
        
        Args:
            save_path: Path to save the plot
        """
        precision, recall, _ = precision_recall_curve(self.y_true, self.y_proba)
        pr_auc = average_precision_score(self.y_true, self.y_proba)
        
        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, label=f'PR Curve (AUC = {pr_auc:.3f})')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Precision-Recall Curve')
        plt.legend()
        plt.grid(True)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_lift_curve(self, save_path: str = None) -> None:
        """
        Plot lift curve.
        
        Args:
            save_path: Path to save the plot
        """
        lift_data = self.calculate_lift()
        
        plt.figure(figsize=(12, 5))
        
        # Lift by decile
        plt.subplot(1, 2, 1)
        plt.bar(lift_data['decile'], lift_data['lift'])
        plt.xlabel('Decile')
        plt.ylabel('Lift')
        plt.title('Lift by Decile')
        plt.axhline(y=1, color='r', linestyle='--', label='Baseline')
        plt.legend()
        
        # Cumulative lift
        plt.subplot(1, 2, 2)
        plt.plot(lift_data['decile'], lift_data['cumulative_lift'], marker='o')
        plt.xlabel('Decile')
        plt.ylabel('Cumulative Lift')
        plt.title('Cumulative Lift')
        plt.axhline(y=1, color='r', linestyle='--', label='Baseline')
        plt.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_calibration_curve(self, save_path: str = None) -> None:
        """
        Plot calibration curve.
        
        Args:
            save_path: Path to save the plot
        """
        fraction_of_positives, mean_predicted_value = calibration_curve(
            self.y_true, self.y_proba, n_bins=10
        )
        
        plt.figure(figsize=(8, 6))
        plt.plot(mean_predicted_value, fraction_of_positives, "s-", label="Model")
        plt.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")
        plt.xlabel('Mean Predicted Probability')
        plt.ylabel('Fraction of Positives')
        plt.title('Calibration Curve')
        plt.legend()
        plt.grid(True)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_confusion_matrix(self, save_path: str = None) -> None:
        """
        Plot confusion matrix.
        
        Args:
            save_path: Path to save the plot
        """
        cm = confusion_matrix(self.y_true, self.y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.title('Confusion Matrix')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_interactive_dashboard(self, save_path: str = None) -> None:
        """
        Create interactive dashboard with Plotly.
        
        Args:
            save_path: Path to save the HTML file
        """
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('ROC Curve', 'Precision-Recall Curve', 
                          'Lift Curve', 'Calibration Curve'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # ROC Curve
        fpr, tpr, _ = roc_curve(self.y_true, self.y_proba)
        auc = roc_auc_score(self.y_true, self.y_proba)
        fig.add_trace(
            go.Scatter(x=fpr, y=tpr, name=f'ROC (AUC={auc:.3f})'),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=[0, 1], y=[0, 1], name='Random', line=dict(dash='dash')),
            row=1, col=1
        )
        
        # Precision-Recall Curve
        precision, recall, _ = precision_recall_curve(self.y_true, self.y_proba)
        pr_auc = average_precision_score(self.y_true, self.y_proba)
        fig.add_trace(
            go.Scatter(x=recall, y=precision, name=f'PR (AUC={pr_auc:.3f})'),
            row=1, col=2
        )
        
        # Lift Curve
        lift_data = self.calculate_lift()
        fig.add_trace(
            go.Bar(x=lift_data['decile'], y=lift_data['lift'], name='Lift'),
            row=2, col=1
        )
        
        # Calibration Curve
        fraction_of_positives, mean_predicted_value = calibration_curve(
            self.y_true, self.y_proba, n_bins=10
        )
        fig.add_trace(
            go.Scatter(x=mean_predicted_value, y=fraction_of_positives, 
                      mode='markers+lines', name='Calibration'),
            row=2, col=2
        )
        fig.add_trace(
            go.Scatter(x=[0, 1], y=[0, 1], name='Perfect', line=dict(dash='dash')),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(height=800, title_text="Model Evaluation Dashboard")
        
        if save_path:
            fig.write_html(save_path)
        
        fig.show()
    
    def generate_report(self) -> str:
        """
        Generate comprehensive evaluation report.
        
        Returns:
            Report string
        """
        # Calculate all metrics
        basic_metrics = self.calculate_basic_metrics()
        precision_at_k = self.calculate_precision_at_k()
        recall_at_k = self.calculate_recall_at_k()
        business_metrics = self.calculate_business_metrics()
        
        # Generate report
        report = f"""
        MODEL EVALUATION REPORT
        =======================
        
        Basic Metrics:
        - Accuracy: {basic_metrics['accuracy']:.3f}
        - Precision: {basic_metrics['precision']:.3f}
        - Recall: {basic_metrics['recall']:.3f}
        - F1-Score: {basic_metrics['f1_score']:.3f}
        - ROC-AUC: {basic_metrics['roc_auc']:.3f}
        - PR-AUC: {basic_metrics['pr_auc']:.3f}
        
        Precision at K:
        """
        
        for k, precision in precision_at_k.items():
            report += f"- Precision@{k}: {precision:.3f}\n"
        
        report += "\nRecall at K:\n"
        for k, recall in recall_at_k.items():
            report += f"- Recall@{k}: {recall:.3f}\n"
        
        report += "\nBusiness Metrics:\n"
        for metric, value in business_metrics.items():
            report += f"- {metric}: {value:.2f}\n"
        
        return report


def compare_models(model_results: Dict[str, Dict], save_path: str = None) -> None:
    """
    Compare multiple models.
    
    Args:
        model_results: Dictionary of model results
        save_path: Path to save the comparison plot
    """
    metrics = ['roc_auc', 'pr_auc', 'precision', 'recall', 'f1_score']
    
    comparison_data = []
    for model_name, results in model_results.items():
        for metric in metrics:
            if metric in results:
                comparison_data.append({
                    'Model': model_name,
                    'Metric': metric,
                    'Value': results[metric]
                })
    
    df = pd.DataFrame(comparison_data)
    
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df, x='Metric', y='Value', hue='Model')
    plt.title('Model Comparison')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()
