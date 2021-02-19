/**
 * Calls a function repetitively until either the result is valid or the
 * maximum number of network errors is reached.
 *
 * @template T
 * @param {function(): Promise<T>} fn The function to be polled.
 * @param {function(T): boolean} validate Function to validate fn’s result.
 * @param {number} interval Interval in milliseconds.
 * @param {number} maxConsecutiveNetworkErrors The maximum number of network
 *     errors after which the polling should stop.
 * @returns {Promise<T>}
 */
async function poll({ fn, validate, interval, maxConsecutiveNetworkErrors }) {
  let result = null;
  let consecutiveNetworkErrors = 0;

  const executePoll = async (resolve, reject) => {
    try {
      result = await fn();
      consecutiveNetworkErrors = 0;
    } catch (error) {
      result = null;
      if (error.message.includes("NetworkError")) {
        consecutiveNetworkErrors++;
        if (
          maxConsecutiveNetworkErrors &&
          consecutiveNetworkErrors === maxConsecutiveNetworkErrors
        ) {
          return reject(error);
        }
      }
    }

    if (validate(result)) {
      return resolve(result);
    } else {
      setTimeout(executePoll, interval, resolve, reject);
    }
  };

  return new Promise(executePoll);
}
