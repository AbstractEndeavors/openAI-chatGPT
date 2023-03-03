import { FeedbackTypeNo, PromptTemplatesType } from './enums.js';
import { hideModal } from './utils.js';

/**
 * Create modal to report feedback for a prompt
 *
 * @param {number} PromptIndex
 * @param {PromptTemplatesType} CurrentPromptTemplatesType
 * @param {import('./inject.js').Prompt[]} PromptTemplates
 * @param {function(Event)} reportPrompt
 */
const createReportPromptModal = function (
  PromptIndex,
  CurrentPromptTemplatesType,
  PromptTemplates,
  reportPrompt
) {
  // cannot report own prompts
  if (CurrentPromptTemplatesType === PromptTemplatesType.OWN) {
    return;
  }

  const prompt = PromptTemplates[PromptIndex];

  // prompt does not exist
  if (!prompt) {
    return;
  }

  let reportPromptModal = document.getElementById('reportPromptModal');

  // if modal does not exist, create it, add event listener on submit and append it to body
  if (!reportPromptModal) {
    reportPromptModal = document.createElement('div');
    reportPromptModal.id = 'reportPromptModal';

    reportPromptModal.addEventListener('submit', reportPrompt);

    document.body.appendChild(reportPromptModal);
  }

  reportPromptModal.innerHTML = /*html*/ `
      <div class="fixed inset-0 text-center transition-opacity z-50">
        <div class="absolute bg-gray-900 inset-0 opacity-90">
        </div>

        <div class="fixed inset-0 overflow-y-auto">
          <div class="flex items-center justify-center min-h-full">
            <div
              class="align-center bg-white dark:bg-gray-800 dark:text-gray-200 inline-block overflow-hidden sm:rounded-lg shadow-xl sm:align-middle sm:max-w-lg sm:my-8 sm:w-full text-left transform transition-all"
              role="dialog" aria-modal="true" aria-labelledby="modal-headline" style="text-align: left;">

              <div class="bg-white dark:bg-gray-800 px-4 pt-5 pb-4 sm:p-6 sm:pb-4">

                <div id="reportPromptIntroText">
                  <p class="mb-6">
                    Thanks for helping us improve.<br><br>

                    We need you to answer a few questions so we can better understand what's going on with this Prompt.<br><br>

                    You'll also have the option to add more info in your own words and add more details to the report.<br><br>

                    We take reports seriously.<br><br>

                    If we find a rule violation, we'll either remove the Prompt immediately or ask them to revise, or lock or suspend the account.
                  </p>

                  <div class="mt-2">
                    <label for="FeedbackTypeNo" class="block">What would you like to report?</label>
                    <select data-prompt-id="${prompt.ID}" id="FeedbackTypeNo" name="FeedbackTypeNo" class="mt-2 mb-3 dark:bg-gray-700 dark:border-gray-700 dark:hover:bg-gray-900 rounded w-full" required>
                      <option value="${FeedbackTypeNo.GENERIC_LEGAL_CONCERN}">
                      Legal concerns
                      </option>
                      <optgroup label="Result concerns">                        
                        <option value="${FeedbackTypeNo.NOT_MULTILINGUAL}">
                          Result in wrong language
                        </option>
                        <option value="${FeedbackTypeNo.NOT_GENERIC}">
                          Result on wrong topic/keywords
                        </option>                        
                        <option value="${FeedbackTypeNo.GENERIC_CONCERN}">
                          Prompt not working as expected
                        </option>
                      </optgroup>                  
                      <option value="${FeedbackTypeNo.SPAM}">Spam</option>
                    </select>
                  </div>
                </div>

                <div class="reportPromptFeedbackContainer hidden overflow-y-auto" id="reportPromptFeedbackForm"></div>
              </div>

              <div class="bg-gray-200 dark:bg-gray-700 px-4 py-3 text-right">
                <button type="button" class="bg-gray-600 hover:bg-gray-800 mr-2 px-4 py-2 rounded text-white"
                        onclick="AIPRM.hideModal('reportPromptModal')"> Cancel
                </button>
                <button type="button" id="reportPromptSubmitButton" class="bg-green-600 hover:bg-green-700 mr-2 px-4 py-2 rounded text-white">Start Report
                </button>
              </div>
            </div>
          </div>
        </div>

      </div>`;

  // add event listener to change button text and type on click
  reportPromptModal.querySelector('#reportPromptSubmitButton').addEventListener(
    'click',
    (e) => {
      // hide intro text
      document.getElementById('reportPromptIntroText').style = 'display: none;';

      const feedbackTypeNoSelect = document.getElementById('FeedbackTypeNo');

      // show feedback type specific text & form
      const feedbackForm = document.getElementById('reportPromptFeedbackForm');

      feedbackForm.innerHTML = getFeedbackFormTemplate(
        +feedbackTypeNoSelect.value,
        feedbackTypeNoSelect.dataset.promptId
      );

      feedbackForm.classList.remove('hidden');

      // change button text to "Send Report" and replace event listener
      e.target.innerText = 'Send Report';

      e.target.addEventListener('click', () => {
        // submit the visible form in reportPromptModal
        document
          .querySelector(
            '#reportPromptModal .reportPromptFeedbackContainer:not(.hidden) form'
          )
          .requestSubmit();
      });
    },
    { once: true }
  );

  reportPromptModal.style = 'display: block;';

  // add event listener to close the modal on ESC
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      hideModal('reportPromptModal');
    }
  });
};

/**
 * Get the feedback form template for a specific feedback type
 * 
 * @param {FeedbackTypeNo} selectedFeedbackTypeNo
 * @param {string} promptID
 * @returns {string} - HTML string
 s*/
const getFeedbackFormTemplate = (selectedFeedbackTypeNo, promptID) => {
  const requiresFeedbackContactText = [
    FeedbackTypeNo.GENERIC_CONCERN,
    FeedbackTypeNo.GENERIC_LEGAL_CONCERN,
  ].includes(selectedFeedbackTypeNo);

  return /*html*/ `
    <p class="mb-6">
      Since we are not affiliated with OpenAI or ChatGPT,
      we are not responsible for the output of ChatGPT.<br><br>

      ${
        selectedFeedbackTypeNo === FeedbackTypeNo.GENERIC_CONCERN
          ? /*html*/ `
          But we can try to help you with results.<br><br>

          We can do this by looking at the prompt reported,
          and the output generated.
        `
          : 'But we will take your report about the prompt and evaluate it.'
      }
    </p>

    <form>
      <input type="hidden" name="PromptID" value="${promptID}" />

      ${
        selectedFeedbackTypeNo !== FeedbackTypeNo.GENERIC_CONCERN
          ? /*html*/ `<input type="hidden" name="FeedbackTypeNo" value="${selectedFeedbackTypeNo}" />`
          : ''
      }

      <label>Contact Email${
        !requiresFeedbackContactText
          ? ' <span class="text-sm text-gray-500">(optional)</span>'
          : ''
      }</label>
      <input name="FeedbackContact" 
        ${requiresFeedbackContactText ? ' required ' : ''} type="email"
        title="Email address to contact you in case we need more information"
        class="w-full bg-gray-100 dark:bg-gray-700 dark:border-gray-700 rounded p-2 mt-2 mb-3"
        placeholder="example@example.com" />

      <label>Feedback${
        !requiresFeedbackContactText
          ? ' <span class="text-sm text-gray-500">(optional)</span>'
          : ''
      }</label>
      <textarea name="FeedbackText" 
        ${requiresFeedbackContactText ? ' required ' : ''}
        title="Short description of the issue"
        class="w-full bg-gray-100 dark:bg-gray-700 dark:border-gray-700 rounded p-2 mt-2 mb-3" style="height: 140px;"
        placeholder="Please describe the issue you are having with this prompt.${
          selectedFeedbackTypeNo === FeedbackTypeNo.GENERIC_CONCERN
            ? ' Please include your full history of the prompt including the original prompt used.'
            : ''
        }"></textarea>

      ${
        selectedFeedbackTypeNo === FeedbackTypeNo.GENERIC_CONCERN
          ? /*html*/ `
            <label class="block">Are you a customer paying for AIPRM support? Would you like to hire us to improve your prompt and create a private prompt specifically for you?</label>
            <select name="FeedbackTypeNo" class="mt-2 mb-3 dark:bg-gray-700 dark:border-gray-700 dark:hover:bg-gray-900 rounded w-full" required>
              <option value="${FeedbackTypeNo.PROMPT_SUPPORT_FREE}">I want free support</option>
              <option value="${FeedbackTypeNo.PROMPT_SUPPORT_WANT_PAID}">I want to pay for support</option>
              <option value="${FeedbackTypeNo.PROMPT_SUPPORT_PAID}">I am already paying for support</option>
            </select>
          `
          : ''
      }
    </form>
  `;
};

export { createReportPromptModal };
