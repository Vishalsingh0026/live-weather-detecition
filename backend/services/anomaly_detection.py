import logging
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import List, Tuple, Dict, Any
from collections import deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AnomalyDetectionService:
    """Service for detecting anomalies in real-time data streams."""

    def __init__(self, window_size: int = 100, contamination: float = 0.1):
        self.window_size = window_size
        self.contamination = contamination
        self.data_buffers = {}  # Store last N values per data feed
        self.scaler = StandardScaler()
        self.models = {}  # Train separate model per feed
        self.thresholds = {}  # Store anomaly thresholds

    def add_data_point(self, feed_id: int, value: float) -> None:
        """Add a new data point to the buffer for a specific feed."""
        if feed_id not in self.data_buffers:
            self.data_buffers[feed_id] = deque(maxlen=self.window_size)

        self.data_buffers[feed_id].append(value)

    def detect_anomaly(
        self, feed_id: int, value: float, method: str = "isolation_forest"
    ) -> Tuple[bool, float, float]:
        """
        Detect if a value is anomalous.

        Returns:
            Tuple of (is_anomalous, anomaly_score, threshold)
        """
        if method == "isolation_forest":
            return self._detect_with_isolation_forest(feed_id, value)
        elif method == "zscore":
            return self._detect_with_zscore(feed_id, value)
        elif method == "mad":
            return self._detect_with_mad(feed_id, value)
        else:
            raise ValueError(f"Unknown anomaly detection method: {method}")

    def _detect_with_isolation_forest(
        self, feed_id: int, value: float
    ) -> Tuple[bool, float, float]:
        """Use Isolation Forest for anomaly detection."""
        self.add_data_point(feed_id, value)

        if feed_id not in self.data_buffers or len(self.data_buffers[feed_id]) < 5:
            # Not enough data
            return False, 0.0, 0.5

        # Prepare data
        data = np.array(list(self.data_buffers[feed_id])).reshape(-1, 1)

        # Train model
        try:
            model = IsolationForest(
                contamination=self.contamination,
                random_state=42,
                n_estimators=100,
            )
            model.fit(data)
            self.models[feed_id] = model

            # Score the latest value
            latest_point = np.array([[value]])
            anomaly_score = model.score_samples(latest_point)[0]  # Negative = anomaly
            prediction = model.predict(latest_point)[0]  # -1 = anomaly, 1 = normal

            # Normalize score to 0-1 (higher = more anomalous)
            normalized_score = 1 / (1 + np.exp(-anomaly_score))
            threshold = 0.5

            is_anomalous = prediction == -1

            self.thresholds[feed_id] = threshold
            logger.info(
                f"Feed {feed_id}: score={normalized_score:.3f}, anomalous={is_anomalous}"
            )

            return is_anomalous, normalized_score, threshold
        except Exception as e:
            logger.error(f"Error in Isolation Forest detection for feed {feed_id}: {e}")
            return False, 0.0, 0.5

    def _detect_with_zscore(
        self, feed_id: int, value: float
    ) -> Tuple[bool, float, float]:
        """Use Z-Score for anomaly detection."""
        self.add_data_point(feed_id, value)

        if feed_id not in self.data_buffers or len(self.data_buffers[feed_id]) < 3:
            return False, 0.0, 3.0

        data = np.array(list(self.data_buffers[feed_id]))
        mean = np.mean(data)
        std = np.std(data)

        if std == 0:
            return False, 0.0, 3.0

        z_score = abs((value - mean) / std)
        threshold = 3.0
        is_anomalous = z_score > threshold

        # Normalize to 0-1
        normalized_score = min(1.0, z_score / threshold)

        return is_anomalous, normalized_score, threshold

    def _detect_with_mad(
        self, feed_id: int, value: float
    ) -> Tuple[bool, float, float]:
        """Use Median Absolute Deviation for anomaly detection."""
        self.add_data_point(feed_id, value)

        if feed_id not in self.data_buffers or len(self.data_buffers[feed_id]) < 3:
            return False, 0.0, 2.5

        data = np.array(list(self.data_buffers[feed_id]))
        median = np.median(data)
        mad = np.median(np.abs(data - median))

        if mad == 0:
            return False, 0.0, 2.5

        modified_z_score = 0.6745 * (value - median) / mad
        threshold = 2.5
        is_anomalous = abs(modified_z_score) > threshold

        normalized_score = min(1.0, abs(modified_z_score) / threshold)

        return is_anomalous, normalized_score, threshold

    def detect_batch_anomalies(
        self, feed_id: int, values: List[float]
    ) -> Dict[int, Dict[str, Any]]:
        """Detect anomalies in a batch of values."""
        results = {}
        for i, value in enumerate(values):
            is_anomalous, score, threshold = self.detect_anomaly(feed_id, value)
            results[i] = {
                "value": value,
                "is_anomalous": is_anomalous,
                "anomaly_score": score,
                "threshold": threshold,
            }
        return results

    def get_anomaly_stats(self, feed_id: int) -> Dict[str, Any]:
        """Get anomaly detection statistics for a feed."""
        if feed_id not in self.data_buffers:
            return {"status": "no_data"}

        data = np.array(list(self.data_buffers[feed_id]))
        return {
            "feed_id": feed_id,
            "buffer_size": len(data),
            "mean": float(np.mean(data)),
            "std": float(np.std(data)),
            "min": float(np.min(data)),
            "max": float(np.max(data)),
            "median": float(np.median(data)),
            "threshold": self.thresholds.get(feed_id, 0.5),
        }

    def clear_buffer(self, feed_id: int) -> None:
        """Clear data buffer for a feed."""
        if feed_id in self.data_buffers:
            self.data_buffers[feed_id].clear()
        if feed_id in self.models:
            del self.models[feed_id]
        if feed_id in self.thresholds:
            del self.thresholds[feed_id]
        logger.info(f"Cleared anomaly detection buffer for feed {feed_id}")


anomaly_detector = AnomalyDetectionService()
