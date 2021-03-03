/**
 * Invokes a Promise repetitively until it resolves to the expected outcome.
 *
 * @template T
 * @param {function(): Promise<T>} fn The function to be polled.
 * @param {function(T): boolean} validate Function to validate fn’s result.
 * @param {number} interval Polling interval in milliseconds.
 * @param {number} [timeout] Time in milliseconds after which to abort.
 * @returns {Promise<T>}
 */
async function poll({ fn, validate, interval, timeout }) {
  const start = new Date().getTime();
  let lastError = null;

  const executePoll = async (resolve, reject) => {
    try {
      const result = await fn();
      if (validate(result)) {
        return resolve(result);
      } else {
        lastError = new Error("Operation timed out.");
      }
    } catch (error) {
      lastError = error;
    }
    const totalTimeElapsed = new Date().getTime() - start;
    if (timeout !== undefined && totalTimeElapsed > timeout) {
      return reject(lastError);
    }
    setTimeout(executePoll, interval, resolve, reject);
  };

  return new Promise(executePoll);
}
