import { APIEndpoint } from './config.js';

/* eslint-disable no-unused-vars */
import {
  ExternalSystemNo,
  VoteTypeNo,
  SortModeNo,
  FeedbackTypeNo,
  MessageVoteTypeNo,
  UsageTypeNo,
  MessageSeverityNo,
  UserStatusNo,
} from './enums.js';
/* eslint-enable */

import FingerprintJS from './fingerprint.js';

import { Reaction } from './rxn.js';

/** @typedef {{MessageID: string, MessageGroupNo: MessageGroupNo, MessageSeverityNo: MessageSeverityNo, MessageStatusNo: MessageStatusNo, MessageSubject: string, MessageBodyHTML: string, OnlyExternalID: string, OnlyExternalSystemNo: ExternalSystemNo, ExpiryTime: string, CreationTime: string}} Message */

const userFootprintVersion = '01';

// generate anonymous user footprint using FingerprintJS to prevent abuse
async function generateUserFootprint() {
  const fpPromise = FingerprintJS.load({
    monitoring: false,
  });

  const fp = await fpPromise;
  const result = await fp.get();

  return `${userFootprintVersion}-${result.visitorId}`;
}

const AIPRMClient = {
  APIEndpoint,

  /** @type {{ExternalID: string, ExternalSystemNo: ExternalSystemNo, Email: string, Name: string, UserStatusNo: UserStatusNo, UserFootprint: string, MaxNewPublicPromptsAllowed: number, MaxNewPrivatePromptsAllowed: number}} */
  User: null,

  // fetch the user profile from ChatGPT session API endpoint
  async init() {
    const UserFootprint = await generateUserFootprint();

    return (
      fetch('/api/auth/session')
        // check if the response is OK
        .then((response) => {
          if (response.ok) {
            // parse the JSON response
            return response.json();
          }
          throw new Error('Network response was not OK.');
        })
        // set the user object
        .then((res) => {
          this.User = {
            // Send the anonymous, not identifiable OpenAI hashed user ID to AIPRM to link the user to his own prompts
            ExternalID: res.user.id,
            ExternalSystemNo: ExternalSystemNo.OPENAI,
            // So far no reason to send email and name to AIPRM. This may change in the future, but needs consent from the user.
            // Email: res.user.email,
            // Name: res.user.name,
            UserStatusNo: UserStatusNo.UNKNOWN,
            UserFootprint,
            MaxNewPrivatePromptsAllowed: 0,
            MaxNewPublicPromptsAllowed: 0,
          };
        })
        // check user status
        .then(() => this.checkUserStatus())
    );
  },

  // check the user status using AIPRM API endpoint
  checkUserStatus() {
    if (!this.User) {
      return;
    }

    return (
      fetch(
        `${this.APIEndpoint}/Users/Status?ExternalID=${this.User.ExternalID}&ExternalSystemNo=${this.User.ExternalSystemNo}`
      )
        // check if the response is OK
        .then((response) => {
          if (response.ok) {
            // parse the JSON response
            return response.json();
          }
          throw new Error('Network response was not OK.');
        })
        // set the user status
        .then((res) => {
          if (!Object.prototype.hasOwnProperty.call(res, 'UserStatusNo')) {
            throw new Error(
              'User status response is missing UserStatusNo property.'
            );
          }

          this.User.UserStatusNo = res.UserStatusNo;

          if (
            Object.prototype.hasOwnProperty.call(
              res,
              'MaxNewPrivatePromptsAllowed'
            )
          ) {
            this.User.MaxNewPrivatePromptsAllowed =
              res.MaxNewPrivatePromptsAllowed;
          }

          if (
            Object.prototype.hasOwnProperty.call(
              res,
              'MaxNewPublicPromptsAllowed'
            )
          ) {
            this.User.MaxNewPublicPromptsAllowed =
              res.MaxNewPublicPromptsAllowed;
          }
        })
    );
  },

  // save the prompt using AIPRM API endpoint
  savePrompt(prompt) {
    return (
      fetch(`${this.APIEndpoint}/Prompts${prompt.ID ? '/' + prompt.ID : ''}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...prompt,
          User: this.User,
        }),
      })
        .then((response) => {
          return Promise.all([response.json(), response]);
        })
        // check if the response is OK
        .then(([json, response]) => {
          if (response.ok) {
            // parse the JSON response
            return json;
          }

          if (json && json.ReactionNo) {
            throw Reaction.mapReactionNo(json.ReactionNo);
          }

          throw new Error('Network response was not OK.');
        })
    );
  },

  /**
   * Fetch the prompt from AIPRM API endpoint
   *
   * @param {string} PromptID
   * @returns {Promise<Prompt>}
   */
  getPrompt(PromptID) {
    return (
      fetch(
        `${this.APIEndpoint}/Prompts/${PromptID}?ExternalID=${this.User.ExternalID}&ExternalSystemNo=${this.User.ExternalSystemNo}`
      )
        // check if response is OK
        .then((res) => {
          if (!res.ok) {
            throw new Error('Network response was not OK');
          }
          return res;
        })
        // parse response as JSON
        .then((res) => res.json())
    );
  },

  /**
   * vote for a prompt using AIPRM API endpoint
   *
   * @param {string} PromptID
   * @param {(1|-1)} Vote
   */
  voteForPrompt(PromptID, Vote) {
    return (
      fetch(`${this.APIEndpoint}/Vote/${PromptID}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          VoteTypeNo: VoteTypeNo.PROMPT_TEASER_THUMBS,
          Vote: Vote,
          User: this.User,
        }),
      })
        // check if response is OK
        .then((res) => {
          if (!res.ok) {
            throw new Error('Network response was not OK');
          }

          return res;
        })
    );
  },

  /**
   * Report a prompt using AIPRM API endpoint
   *
   * @param {string} PromptID
   * @param {FeedbackTypeNo} FeedbackTypeNo
   * @param {string} FeedbackText
   * @param {string} FeedbackContact
   */
  reportPrompt(PromptID, FeedbackTypeNo, FeedbackText, FeedbackContact) {
    return (
      fetch(`${this.APIEndpoint}/Prompts/${PromptID}/Feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          FeedbackContact,
          FeedbackText,
          FeedbackTypeNo,
          User: this.User,
        }),
      })
        // check if response is OK
        .then((res) => {
          if (!res.ok) {
            throw new Error('Network response was not OK');
          }

          return res;
        })
    );
  },

  /**
   * Track prompt usage using AIPRM API endpoint
   *
   * @param {string} PromptID
   * @param {UsageTypeNo} UsageTypeNo
   */
  usePrompt(PromptID, UsageTypeNo = UsageTypeNo.CLICK) {
    return (
      fetch(`${this.APIEndpoint}/Prompts/${PromptID}/Use`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          UsageTypeNo: UsageTypeNo,
          User: this.User,
        }),
      })
        // check if response is OK
        .then((res) => {
          if (!res.ok) {
            throw new Error('Network response was not OK');
          }

          return res;
        })
    );
  },

  // delete prompt using AIPRM API endpoint
  deletePrompt(PromptID) {
    return (
      fetch(
        `${this.APIEndpoint}/Prompts/${PromptID}?ExternalID=${this.User.ExternalID}&ExternalSystemNo=${this.User.ExternalSystemNo}&UserFootprint=${this.User.UserFootprint}`,
        {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            User: this.User,
          }),
        }
      )
        // check if response is OK
        .then((res) => {
          if (!res.ok) {
            throw new Error('Network response was not OK');
          }
        })
    );
  },

  /**
   * Fetch the prompts using AIPRM API endpoint
   *
   * @param {string} Community Topic ID e.g. "SEO-84c5d6a7b8e9f0c1"
   * @param {SortModeNo} SortModeNo
   * @param {number} Limit
   * @param {number} Offset
   */
  getPrompts(
    Community,
    SortModeNo = SortModeNo.TOP_VOTES,
    Limit = 10,
    Offset = 0
  ) {
    return (
      fetch(
        `${this.APIEndpoint}/Prompts?Community=${Community}&Limit=${Limit}&Offset=${Offset}&OwnerExternalID=${this.User.ExternalID}&OwnerExternalSystemNo=${this.User.ExternalSystemNo}&SortModeNo=${SortModeNo}`
      )
        // check if response is OK
        .then((res) => {
          if (!res.ok) {
            throw new Error('Network response was not OK');
          }

          return res;
        })
        // parse response as JSON
        .then((res) => res.json())
    );
  },

  /**
   * Get messages using AIPRM API endpoint
   *
   * @param {string} Community Topic ID e.g. "SEO-84c5d6a7b8e9f0c1"
   * @returns {Promise<Message[]>}
   */
  getMessages(Community) {
    return (
      fetch(
        `${this.APIEndpoint}/Messages?Community=${Community}&ExternalID=${this.User.ExternalID}&ExternalSystemNo=${this.User.ExternalSystemNo}`
      )
        // check if response is OK
        .then((res) => {
          if (!res.ok) {
            throw new Error('Network response was not OK');
          }

          return res;
        })
        // parse response as JSON
        .then((res) => res.json())
    );
  },

  /**
   * Vote for a message using AIPRM API endpoint
   *
   * @param {string} MessageID
   * @param {MessageVoteTypeNo} VoteTypeNo
   */
  voteForMessage(MessageID, VoteTypeNo) {
    return (
      fetch(`${this.APIEndpoint}/Vote/${MessageID}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          VoteTypeNo: VoteTypeNo,
          Vote: VoteTypeNo === MessageVoteTypeNo.MESSAGE_DISLIKE ? -1 : 1,
          User: this.User,
        }),
      })
        // check if response is OK
        .then((res) => {
          if (!res.ok) {
            throw new Error('Network response was not OK');
          }

          return res;
        })
    );
  },

  /**
   * Confirm a message using AIPRM API endpoint
   *
   * @param {string} MessageID
   */
  confirmMessage(MessageID) {
    return (
      fetch(`${this.APIEndpoint}/Vote/${MessageID}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          VoteTypeNo: VoteTypeNo.MESSAGE_CONFIRM,
          Vote: 1,
          User: this.User,
        }),
      })
        // check if response is OK
        .then((res) => {
          if (!res.ok) {
            throw new Error('Network response was not OK');
          }

          return res;
        })
    );
  },
};

export { AIPRMClient, Reaction };
