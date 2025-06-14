/**
 * Calculates the user's score based on AI prediction accuracy (lower accuracy = higher score).
 * @param {number} score - AI's prediction score (expected 0-100).
 * @param {number} maxPoints - Maximum possible points per prompt (default: 10).
 * @returns {number} The score the user earns for this prompt.
 */
export const calculateUserPoints = (
  score: number,
  maxPoints: number = 10
): number => {
  if (score < 0 || score > 100) {
    console.error("Score out of bounds:", score);
    score = Math.max(0, Math.min(100, score)); // Clamp between 0 and 100
  }
  const returnedPoints = maxPoints * (1 - score / 100);
  // round to the nearest integer
  return Math.round(returnedPoints);
};

/**
 * Calculates the progress increment based on AI prediction accuracy.
 * Uses a square root scale to make progress increase slower at higher accuracies.
 * @param {number} accuracy - AI's prediction accuracy (expected 0-100).
 * @param {number} maxIncrement - Maximum possible increment per prompt (default: 10).
 * @returns {number} The progress increment to add to the training bar.
 */
export const calculateProgressIncrement = (
  accuracy: number,
  maxIncrement: number = 10
): number => {
  if (accuracy < 0 || accuracy > 100) {
    console.error("Accuracy out of bounds:", accuracy);
    accuracy = Math.max(0, Math.min(100, accuracy)); // Clamp between 0 and 100
  }
  // Scale accuracy to 0-1, take square root, then scale by maxIncrement
  const increment = Math.sqrt(accuracy / 100) * maxIncrement;
  return Math.round(increment); // Round to the nearest integer
};

// You could add other scoring-related functions here in the future.
