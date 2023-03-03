/* eslint-disable no-unused-vars */
import {
  MessageSeverityNo,
  MessageStatusNo,
  MessageVoteTypeNo,
} from './enums.js';
/* eslint-enable */

import { hideModal, svg } from './utils.js';

// Mapping of MessageSeverityNo to the corresponding CSS class name for the notification message
const NotificationMessageSeverityClassName = {
  [MessageSeverityNo.INFO]: 'bg-gray-500',
  [MessageSeverityNo.SUCCESS]: 'bg-green-500',
  [MessageSeverityNo.UPDATE]: 'bg-[#5436DA]',
};

/**
 * Show the first active and not expired message with MessageSeverityNo.MANDATORY_MUST_CONFIRM (if any)
 * otherwise show the first active and not expired message with other MessageSeverityNo (if any)
 *
 * @param {import("./client").Message[]} messages
 * @param {(MessageID: string)} confirmCallback
 * @param {(MessageID: string, Vote: MessageVoteTypeNo)} voteCallback
 */
const showMessage = (messages, confirmCallback, voteCallback) => {
  // get the first active and not expired message with MessageSeverityNo.MANDATORY_MUST_CONFIRM
  let message = messages.find(
    (message) =>
      message.MessageStatusNo === MessageStatusNo.ACTIVE &&
      message.MessageSeverityNo === MessageSeverityNo.MANDATORY_MUST_CONFIRM &&
      (!message.ExpiryTime || new Date(message.ExpiryTime) > new Date())
  );

  // if there is a message with MessageSeverityNo.MANDATORY_MUST_CONFIRM, show it
  if (message) {
    createConfirmMessageModal(message, confirmCallback);

    return;
  }

  // otherwise, get the first active and not expired message with other MessageSeverityNo (if any)
  message = messages.find(
    (message) =>
      message.MessageStatusNo === MessageStatusNo.ACTIVE &&
      message.MessageSeverityNo !== MessageSeverityNo.MANDATORY_MUST_CONFIRM &&
      (!message.ExpiryTime || new Date(message.ExpiryTime) > new Date())
  );

  // if there is no message, return - otherwise show it
  if (!message) {
    return;
  }

  createNotificationMessage(message, voteCallback);
};

/**
 * Create a modal to confirm a message with MessageSeverityNo.MANDATORY_MUST_CONFIRM
 *
 * @param {import("./client").Message} message
 * @param {(MessageID: string)} confirmCallback
 */
const createConfirmMessageModal = (message, confirmCallback) => {
  let confirmMessageModal = document.getElementById('confirmMessageModal');

  // if modal does not exist, create it, add event listener on submit and append it to body
  if (!confirmMessageModal) {
    confirmMessageModal = document.createElement('div');
    confirmMessageModal.id = 'confirmMessageModal';

    // add event listener on submit to call confirmCallback and hide modal on success
    confirmMessageModal.addEventListener('submit', async (e) => {
      e.preventDefault();

      const MessageID = e.target.MessageID.value;

      if (await confirmCallback(MessageID)) {
        hideModal('confirmMessageModal');
      }
    });

    document.body.appendChild(confirmMessageModal);
  }

  confirmMessageModal.innerHTML = /*html*/ `
      <div class="fixed inset-0 text-center transition-opacity z-50">
        <div class="absolute bg-gray-900 inset-0 opacity-90">
        </div>

        <div class="fixed inset-0 overflow-y-auto">
          <div class="flex items-center justify-center min-h-full">
            <form>
              <div
                class="align-center bg-white dark:bg-gray-800 dark:text-gray-200 inline-block overflow-hidden sm:rounded-lg shadow-xl sm:align-middle sm:max-w-2xl sm:my-8 sm:w-full text-left transform transition-all prose dark:prose-invert"
                role="dialog" aria-modal="true" aria-labelledby="modal-headline" style="text-align: left;">

                <div class="bg-white dark:bg-gray-800 px-4 pt-5 pb-4 sm:p-6 sm:pb-4">

                  <h3 class="mt-1 mb-6">${message.MessageSubject}</h3>

                  <div class="mb-6 overflow-y-auto">${message.MessageBodyHTML}</div>

                  <label class="font-semibold">
                    <input name="MessageID" value="${message.MessageID}" type="checkbox" class="mr-2 dark:bg-gray-700" required> 
                    I read and accept these terms & conditions
                  </label>
                </div>

                <div class="bg-gray-200 dark:bg-gray-700 px-4 py-3 text-right">
                  <button type="submit" id="reportPromptSubmitButton" class="bg-green-600 hover:bg-green-700 mr-2 px-4 py-2 rounded text-white">Confirm
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>

      </div>`;

  confirmMessageModal.style = 'display: block;';
};

/**
 * Create a notification message with thumb up/down buttons
 *
 * @param {import("./client").Message} message
 * @param {(MessageID: string, Vote: MessageVoteTypeNo)} voteCallback
 */
const createNotificationMessage = (message, voteCallback) => {
  const className =
    NotificationMessageSeverityClassName[message.MessageSeverityNo];

  const notificationElement = document.createElement('div');

  notificationElement.innerHTML = /*html*/ `
      <div class="fixed flex justify-center w-full top-2 px-2 z-50 pointer-events-none">
        <div class="${className} flex pointer-events-auto px-6 py-3 rounded-md text-white" role="alert" style="min-width: 30rem;">
          <div class="flex flex-col gap-2 w-full">

            <h4 class="w-full">${message.MessageSubject}</h4>

            <div class="prose w-full text-white">
              ${message.MessageBodyHTML}
            </div> 

            <div class="flex gap-4 mt-4" style="justify-content: end;">
              <button data-message-vote-type-no="${
                MessageVoteTypeNo.MESSAGE_LIKE
              }" title="I like this">${svg('ThumbUp')}</button>
              <button data-message-vote-type-no="${
                MessageVoteTypeNo.MESSAGE_DISLIKE
              }" title="I don't like this">${svg('ThumbDown')}</button>
            </div>

          </div>
        </div>
      </div>
    `;

  // add event listener on like and dislike button to call voteCallback with MessageVoteTypeNo from data attribute and hide notification on success
  notificationElement.querySelectorAll('button').forEach((button) => {
    button.addEventListener('click', async (e) => {
      if (
        await voteCallback(
          message.MessageID,
          +e.target.closest('button').dataset.messageVoteTypeNo
        )
      ) {
        notificationElement.remove();
      }
    });
  });

  document.body.appendChild(notificationElement);
};

export { showMessage };
