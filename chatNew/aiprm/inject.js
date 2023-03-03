import { AIPRMClient, Reaction } from './client.js';

import {
  ActivityFeedURL,
  AppName,
  AppURL,
  ContinueActionsFeedURL,
  EndpointConversation,
  ExportFilePrefix,
  ExportHeaderPrefix,
  LanguageFeedURL,
  PromptPlaceholder,
  TargetLanguagePlaceholder,
  ToneFeedURL,
  TopicFeedURL,
  WritingStyleFeedURL,
} from './config.js';

/* eslint-disable no-unused-vars */
import {
  MessageVoteTypeNo,
  NotificationSeverity,
  PromptTemplatesType,
  PromptTypeNo,
  SortModeNo,
  UsageTypeNo,
  UserStatusNo,
} from './enums.js';
/* eslint-enable */

import { createReportPromptModal } from './feedback.js';
import { showMessage } from './messages.js';

import {
  capitalizeWords,
  css,
  formatDateTime,
  formatAgo,
  formatHumanReadableNumber,
  hideModal,
  sanitizeInput,
  svg,
} from './utils.js';

/**
 * @typedef {Object} Prompt
 * @property {string} ID
 * @property {string} Category - Activity of the prompt (e.g. "Writing")
 * @property {string} Community - Topic of the prompt (e.g. "SEO")
 * @property {string} Prompt - The prompt text
 * @property {string} PromptHint - The prompt hint text (placeholder)
 * @property {PromptTypeNo} PromptTypeNo - public, private or paid prompt
 * @property {string} Title
 * @property {string} Help
 * @property {string} Teaser
 * @property {boolean} OwnPrompt - Whether the prompt is owned by the current user
 * @property {string} RevisionTime
 * @property {string} AuthorName
 * @property {string} AuthorURL
 * @property {number} Usages
 * @property {number} Views
 * @property {number} Votes
 */

/** @typedef {{langcode: string, languageEnglish: string, languageLabel: string}} Language */

/** @typedef {{ID: string, Label: string}} Topic */

/** @typedef {{ID: string, TopicID: string, Label: string}} Activity */

const DefaultPromptActivity = 'all';
const DefaultPromptTopic = 'all';
const DefaultTargetLanguage = 'English*';

const lastPromptTopicKey = 'lastPromptTopic';
const lastTargetLanguageKey = 'lastTargetLanguage';
const lastPageSizeKey = 'lastPageSize';

const queryParamPromptID = 'AIPRM_PromptID';

// The number of prompts per page in the prompt templates section
const pageSizeOptions = [4, 8, 12, 16, 20];
const pageSizeDefault = 12;

const editPromptTemplateEvent = 'editPromptTemplate';

window.AIPRM = {
  // Save a reference to the original fetch function
  fetch: (window._fetch = window._fetch || window.fetch),

  CacheBuster: btoa(new Date().toISOString().slice(0, 16).toString()),

  Client: AIPRMClient,

  // Set default TargetLanguage based on last used language or default to English
  TargetLanguage:
    localStorage.getItem(lastTargetLanguageKey) || DefaultTargetLanguage,

  // Set default Tone
  Tone: null,

  // Set default WritingStyle
  WritingStyle: null,

  // Set default topic
  PromptTopic: localStorage.getItem(lastPromptTopicKey) || DefaultPromptTopic,

  // Set default activity
  PromptActivity: DefaultPromptActivity,

  // Set default sort mode
  /** @type {SortModeNo} */
  PromptSortMode: SortModeNo.TOP_VOTES,

  // Set default search query
  PromptSearch: '',

  // Set default prompt templates type
  /** @type {PromptTemplatesType} */
  PromptTemplatesType: PromptTemplatesType.PUBLIC,

  /** @type {Prompt[]} */
  PromptTemplates: [],

  /** @type {Prompt[]} */
  OwnPrompts: [],

  /** @type {Language[]} */
  Languages: [],

  /** @typedef {{ID: number, Label: string}} Tone */

  /** @type {Tone[]} */
  Tones: [],

  /** @typedef {{ID: number, Label: string}} WritingStyle */

  /** @type {WritingStyle[]} */
  WritingStyles: [],

  /** @typedef {{ID: number, Label: string, Prompt: string}} ContinueAction */

  /** @type {ContinueAction[]} */
  ContinueActions: [],

  /** @type {Topic[]} */
  Topics: [],

  /** @type {Activity[]} */
  Activities: [],

  // true if admin mode is enabled
  AdminMode: false,

  // This object contains properties for the prompt templates section
  PromptTemplateSection: {
    currentPage: 0, // The current page number
    pageSize: +localStorage.getItem(lastPageSizeKey) || pageSizeDefault, // The number of prompts per page
  },

  /** @type {Prompt} */
  SelectedPromptTemplate: null,

  async init() {
    console.log('AIPRM init');

    // Bind event handler for arrow keys
    this.boundHandleArrowKey = this.handleArrowKey.bind(this);

    await this.Client.init();

    this.replaceFetch();

    this.createObserver();

    this.fetchMessages();

    await this.fetchTopics();

    await this.fetchActivities();

    this.fetchPromptTemplates();

    // Wait for languages, tones, writing styles and continue actions
    await Promise.all([
      this.fetchLanguages(),
      this.fetchTones(),
      this.fetchWritingStyles(),
      this.fetchContinueActions(),
    ]);

    this.insertLanguageToneWritingStyleContinueActions();

    this.setupSidebar();

    this.fetchPromptFromDeepLink();

    // on state change (e.g. back button) fetch the prompt from the deep link
    window.addEventListener('popstate', () => {
      this.fetchPromptFromDeepLink();
    });
  },

  // get the prompt ID from the URL and select the prompt template
  async fetchPromptFromDeepLink() {
    // Get the prompt ID from the URL (AIPRM_PromptID)
    const promptID = new URLSearchParams(window.location.search).get(
      queryParamPromptID
    );

    if (!promptID) {
      // If there is no prompt ID in the URL - deselect the prompt template
      this.selectPromptTemplateByIndex(null);

      return;
    }

    // If the prompt is already selected, do nothing
    if (
      this.SelectedPromptTemplate &&
      this.SelectedPromptTemplate.ID === promptID
    ) {
      return;
    }

    let prompt;

    try {
      // Fetch the prompt using the AIPRM API client
      prompt = await this.Client.getPrompt(promptID);
    } catch (error) {
      this.showNotification(
        NotificationSeverity.ERROR,
        'Something went wrong. Please try again.'
      );
      return;
    }

    if (!prompt) {
      return;
    }

    // Select the prompt template
    this.selectPromptTemplate(prompt);
  },

  // Fetch the list of messages from the server
  async fetchMessages() {
    showMessage(
      await this.Client.getMessages(
        this.PromptTopic === DefaultPromptTopic ? '' : this.PromptTopic
      ),
      this.confirmMessage.bind(this),
      this.voteForMessage.bind(this)
    );
  },

  /**
   * Confirm a message using the AIPRM API client
   *
   * @param {string} MessageID
   * @returns {Promise<boolean>} Whether the message was confirmed successfully
   */
  async confirmMessage(MessageID) {
    try {
      await this.Client.confirmMessage(MessageID);
    } catch (error) {
      this.showNotification(
        NotificationSeverity.ERROR,
        'Something went wrong. Please try again.'
      );
      return false;
    }

    this.showNotification(
      NotificationSeverity.SUCCESS,
      'Thanks for the confirmation!'
    );

    return true;
  },

  /**
   * Vote for a message using the AIPRM API client
   *
   * @param {string} MessageID
   * @param {MessageVoteTypeNo} VoteTypeNo
   * @returns boolean Whether the message was voted for successfully
   */
  async voteForMessage(MessageID, VoteTypeNo) {
    try {
      await this.Client.voteForMessage(MessageID, VoteTypeNo);
    } catch (error) {
      this.showNotification(
        NotificationSeverity.ERROR,
        'Something went wrong. Please try again.'
      );
      return false;
    }

    return true;
  },

  // This function sets up the chat sidebar by adding an "Export Button" and modifying
  // the "New Chat" buttons to clear the selected prompt template when clicked
  setupSidebar() {
    // Add the "Export Button" to the sidebar
    this.addExportButton();
    // Get the "New Chat" buttons
    const buttons = this.getNewChatButtons();
    // Set the onclick event for each button to clear the selected prompt template
    buttons.forEach((button) => {
      button.onclick = () => {
        this.selectPromptTemplateByIndex(null);

        // Hide the "Continue Writing" button (no prompt selected/new chat)
        this.hideContinueActionsButton();
      };
    });
  },

  // Fetch the list of topics from a remote CSV file
  async fetchTopics() {
    this.fetch(TopicFeedURL + this.CacheBuster)
      // Convert the response to text
      .then((res) => res.text())
      // Convert the CSV text to an array of records
      .then((csv) => this.CSVToArray(csv))
      // Map the records to topic objects with properties 'ID' and 'Label'
      .then((records) => {
        return (
          records
            .map(([ID, Label]) => {
              return { ID, Label };
            })
            // Filter out records that do not have an ID, or it is the header row (with "ID" as its title)
            .filter(({ ID }) => ID && ID !== 'ID')
        );
      })
      .then((topics) => {
        // Sort and save the topics
        this.Topics = topics.sort((a, b) => a.Label.localeCompare(b.Label));
      });
  },

  // Fetch the list of activities from a remote CSV file
  async fetchActivities() {
    this.fetch(ActivityFeedURL + this.CacheBuster)
      // Convert the response to text
      .then((res) => res.text())
      // Convert the CSV text to an array of records
      .then((csv) => this.CSVToArray(csv))
      // Map the records to activity objects with properties 'TopicID', 'ID', and 'Label'
      .then((records) => {
        return (
          records
            .map(([TopicID, ID, Label]) => {
              return { TopicID, ID, Label };
            })
            // Filter out records that do not have an ID, or it is the header row (with "ID" as its title)
            .filter(({ ID }) => ID && ID !== 'ID')
        );
      })
      .then((activities) => {
        // Sort and save the array of activities
        this.Activities = activities.sort((a, b) =>
          a.Label.localeCompare(b.Label)
        );
      });
  },

  fetchLanguages() {
    // Fetch the list of languages from a remote CSV file
    return (
      this.fetch(LanguageFeedURL + this.CacheBuster)
        // Convert the response to text
        .then((res) => res.text())
        // Convert the CSV text to an array of records
        .then((csv) => this.CSVToArray(csv))
        // Map the records to language objects with properties 'langcode', 'languageEnglish' and 'languageLabel'
        .then((records) => {
          return (
            records
              .map(([langcode, languageEnglish, languageLabel]) => {
                return { langcode, languageEnglish, languageLabel };
              })
              // Filter out records that do not have a language code, or it is the header row (with "langcode" as its title)
              .filter(({ langcode }) => langcode && langcode !== 'langcode')
          );
        })
        .then((languages) => {
          // Save the array of languages to a global variable
          this.Languages = languages;
        })
    );
  },

  // Fetch list of tones from a remote CSV file
  fetchTones() {
    return (
      this.fetch(ToneFeedURL + this.CacheBuster)
        // Convert the response to text
        .then((res) => res.text())
        // Convert the CSV text to an array of records
        .then((csv) => this.CSVToArray(csv))
        // Map the records to tone objects with properties 'ID' and 'Label'
        .then((records) => {
          return (
            records
              .map(([ID, Label]) => {
                return { ID: parseInt(ID), Label };
              })
              // Filter out records that do not have an ID, or it is the header row (with "ID" as its title)
              .filter(({ ID }) => ID && ID !== 'ID')
              // Sort the tones by Label
              .sort((a, b) => a.Label.localeCompare(b.Label))
          );
        })
        .then((tones) => {
          // Save the array of tones to a global variable
          this.Tones = tones;
        })
    );
  },

  // Fetch list of writing styles from a remote CSV file
  fetchWritingStyles() {
    return (
      this.fetch(WritingStyleFeedURL + this.CacheBuster)
        // Convert the response to text
        .then((res) => res.text())
        // Convert the CSV text to an array of records
        .then((csv) => this.CSVToArray(csv))
        // Map the records to writing style objects with properties 'ID' and 'Label'
        .then((records) => {
          return (
            records
              .map(([ID, Label]) => {
                return { ID: parseInt(ID), Label };
              })
              // Filter out records that do not have an ID, or it is the header row (with "ID" as its title)
              .filter(({ ID }) => ID && ID !== 'ID')
              // Sort the writing styles by Label
              .sort((a, b) => a.Label.localeCompare(b.Label))
          );
        })
        .then((writingStyles) => {
          // Save the array of writing styles to a global variable
          this.WritingStyles = writingStyles;
        })
    );
  },

  // Fetch list of continue actions from a remote CSV file
  fetchContinueActions() {
    return (
      this.fetch(ContinueActionsFeedURL + this.CacheBuster)
        // Convert the response to text
        .then((res) => res.text())
        // Convert the CSV text to an array of records
        .then((csv) => this.CSVToArray(csv))
        // Map the records to continue action objects with properties 'ID', 'Label, and 'Prompt'
        .then((records) => {
          return (
            records
              .map(([ID, Label, Prompt]) => {
                return { ID: parseInt(ID), Label, Prompt };
              })
              // Filter out records that do not have an ID, or it is the header row (with "ID" as its title)
              .filter(({ ID }) => ID && ID !== 'ID')
              // Sort the continue actions alphabetically
              .sort((a, b) => a.Label.localeCompare(b.Label))
          );
        })
        .then((continueActions) => {
          // Save the array of continue actions to a global variable
          this.ContinueActions = continueActions;
        })
    );
  },

  async fetchPromptTemplates() {
    /** @type {Prompt[]} */
    const templates = await this.Client.getPrompts(
      this.PromptTopic === DefaultPromptTopic ? '' : this.PromptTopic,
      this.PromptSortMode
    );

    // split templates into public and own
    [this.PromptTemplates, this.OwnPrompts] = templates.reduce(
      (publicPrivatePrompts, template) => {
        // Public template
        if (template.PromptTypeNo === PromptTypeNo.PUBLIC) {
          publicPrivatePrompts[0].push(template);
        }

        // Private or public template owned by current user
        if (template.OwnPrompt) {
          publicPrivatePrompts[1].push(template);
        }

        return publicPrivatePrompts;
      },
      [[], []]
    );

    this.insertPromptTemplatesSection();
  },

  createObserver() {
    // Create a new observer for the chat sidebar to watch for changes to the document body
    const observer = new MutationObserver((mutations) => {
      // For each mutation (change) to the document body
      mutations.forEach((mutation) => {
        // If the mutation is not a change to the list of child nodes, skip it
        if (mutation.type !== 'childList')
          if (mutation.addedNodes.length == 0)
            // If no new nodes were added, skip this mutation
            return;
        // Get the first added node
        const node = mutation.addedNodes[0];
        // If the node is not an element or does not have a `querySelector` method, skip it
        if (!node || !node.querySelector) return;
        // Call the `handleElementAdded` function with the added node
        this.handleElementAdded(node);
      });
    });

    // Start observing the document body for changes
    observer.observe(document.body, { subtree: true, childList: true });
  },

  replaceFetch() {
    window.fetch = (...t) => {
      // If the request is not for the chat backend API, just use the original fetch function
      if (t[0] !== EndpointConversation) return this.fetch(...t);

      // If no prompt template, tone, writing style or target language has been selected, use the original fetch function
      if (
        !this.SelectedPromptTemplate &&
        !this.Tone &&
        !this.WritingStyle &&
        !this.TargetLanguage
      ) {
        return this.fetch(...t);
      }

      // Get the selected prompt template
      const template = this.SelectedPromptTemplate;

      if (template) {
        this.Client.usePrompt(template.ID, UsageTypeNo.SEND);
      }

      // Allow the user to use continue actions after sending a prompt
      this.showContinueActionsButton();

      try {
        // Get the options object for the request, which includes the request body
        const options = t[1];
        // Parse the request body from JSON
        const body = JSON.parse(options.body);

        if (template) {
          // Get the prompt from the request body
          const prompt = body.messages[0].content.parts[0];

          // Use the default target language if no target language has been selected
          const targetLanguage = (
            this.TargetLanguage ? this.TargetLanguage : DefaultTargetLanguage
          ).replace('*', '');

          // Replace the prompt in the request body with the selected prompt template,
          // inserting the original prompt into the template and replacing the target language placeholder
          body.messages[0].content.parts[0] = template.Prompt.replaceAll(
            PromptPlaceholder,
            prompt
          ).replaceAll(TargetLanguagePlaceholder, targetLanguage);
        }

        /** @type {string[]} */
        const toneWritingStyleLanguagePrompt = [];

        // If the user has selected a tone, add it to the request body
        const tone = this.Tone
          ? this.Tones.find((tone) => tone.ID === this.Tone)
          : null;

        if (tone) {
          toneWritingStyleLanguagePrompt.push(
            `${tone.Label.toLowerCase()} tone`
          );

          // Track the tone usage
          this.Client.usePrompt(`${tone.ID}`, UsageTypeNo.SEND);
        }

        // If the user has selected a writing style, add it to the request body
        const writingStyle = this.WritingStyle
          ? this.WritingStyles.find(
              (writingStyle) => writingStyle.ID === this.WritingStyle
            )
          : null;

        if (writingStyle) {
          toneWritingStyleLanguagePrompt.push(
            `${writingStyle.Label.toLowerCase()} writing style`
          );

          // Track the writing style usage
          this.Client.usePrompt(`${writingStyle.ID}`, UsageTypeNo.SEND);
        }

        // If the user has selected a target language, add it to the request body
        if (!template && this.TargetLanguage) {
          toneWritingStyleLanguagePrompt.push(
            `${this.TargetLanguage.replace('*', '')} language`
          );
        }

        // If the user has selected a tone, writing style or target language, add a prompt to the request body
        if (toneWritingStyleLanguagePrompt.length > 0) {
          body.messages[0].content.parts[0] += `\n\nPlease write in ${toneWritingStyleLanguagePrompt.join(
            ', '
          )}.`;
        }

        // Clear the selected prompt template
        this.selectPromptTemplateByIndex(null);
        // Stringify the modified request body and update the options object
        options.body = JSON.stringify(body);
        // Use the modified fetch function to make the request
        return this.fetch(t[0], options);
      } catch {
        // If there was an error parsing the request body or modifying the request,
        // just use the original fetch function
        return this.fetch(...t);
      }
    };
  },

  // This function is called for each new element added to the document body
  handleElementAdded(e) {
    // If the element added is the root element for the chat sidebar, set up the sidebar
    if (e.id === 'headlessui-portal-root') {
      this.setupSidebar();
      return;
    }

    // Disable "Export Button" when no chat were started.
    // Insert "Prompt Templates" section to the main page.
    // Insert language select and continue button above the prompt textarea input
    if (e.querySelector('h1.text-4xl')) {
      this.insertPromptTemplatesSection();
      const button = document.getElementById('export-button');
      if (button) button.style = 'pointer-events: none;opacity: 0.5';

      this.insertLanguageToneWritingStyleContinueActions();
    }

    // Enable "Export Button" when a new chat started.
    // Insert language select and continue button above the prompt textarea input
    if (document.querySelector('.xl\\:max-w-3xl')) {
      const button = document.getElementById('export-button');
      if (button) button.style = '';

      this.insertLanguageToneWritingStyleContinueActions();
    }

    // Add "Save prompt as template" button, if new prompt was added
    if (document.querySelector('.whitespace-pre-wrap')) {
      this.insertSavePromptAsTemplateButton();
    }
  },

  // Add "Save prompt as template" button to the user prompt container next to the "Edit" button
  insertSavePromptAsTemplateButton() {
    // get the first element with selector '.flex.flex-col.items-center .whitespace-pre-wrap' and no children elements
    const firstPrompt = document.querySelector(
      '.flex.flex-col.items-center .whitespace-pre-wrap:not(:has(*))'
    );

    if (!firstPrompt) {
      return;
    }

    // get parent element of the first prompt to find the "Edit" button
    const button =
      firstPrompt.parentElement.parentElement.querySelector('button');

    if (!button) {
      return;
    }

    // Allow user to continue writing from chat history
    this.showContinueActionsButton();

    let saveButton = button.parentElement.querySelector('.save-prompt-button');

    // if button already exists, skip
    if (saveButton) {
      return;
    }

    saveButton = document.createElement('button');
    saveButton.className =
      'save-prompt-button p-1 rounded-md hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-200 disabled:dark:hover:text-gray-400 md:invisible md:group-hover:visible';
    saveButton.title = 'Save prompt as template';
    saveButton.addEventListener('click', this.showSavePromptModal.bind(this));
    saveButton.innerHTML = svg('Save');

    // add HTML before children in button.parentElement
    button.parentElement.prepend(saveButton);
  },

  // get all available activities for the selected topic
  getActivities(TopicID = DefaultPromptTopic) {
    const currentActivities = this.Activities.filter(
      (activity) =>
        !TopicID ||
        TopicID === DefaultPromptTopic ||
        activity.TopicID === TopicID
    );

    // keep only unique activity.Label and extract activity.ID and activity.Label
    return [
      ...new Set(currentActivities.map((activity) => activity.Label)),
    ].map((label) => ({
      ID: this.Activities.find((activity) => activity.Label === label).ID,
      Label: label,
    }));
  },

  /**
   * Validate prompt template before saving
   *
   * @param {Prompt} prompt
   * @returns {boolean} true if prompt is valid
   */
  validatePrompt(prompt) {
    const errors = [];

    // find existing prompt based on ID in PromptTemplates or OwnPrompts
    const existingPrompt = [...this.PromptTemplates, ...this.OwnPrompts].find(
      (p) => p.ID === prompt.ID
    );

    // prompt type was changed between public and private
    const promptTypeChanged =
      existingPrompt && existingPrompt.PromptTypeNo !== prompt.PromptTypeNo;

    // current user cannot create any prompt template, but can edit existing prompt
    if (!this.canCreatePromptTemplate() && !existingPrompt) {
      this.cannotCreatePromptTemplateError();

      return;
    }

    // current user cannot create public prompt template, but can edit existing public prompt template
    if (
      prompt.PromptTypeNo === PromptTypeNo.PUBLIC &&
      !this.canCreatePublicPromptTemplate() &&
      (!existingPrompt || promptTypeChanged)
    ) {
      this.cannotCreatePublicPromptTemplateError();

      return;
    }

    // current user cannot create private prompt template, but can edit existing private prompt template
    if (
      prompt.PromptTypeNo === PromptTypeNo.PRIVATE &&
      !this.canCreatePrivatePromptTemplate() &&
      (!existingPrompt || promptTypeChanged)
    ) {
      this.cannotCreatePrivatePromptTemplateError();

      return;
    }

    // require AuthorName and AuthorURL if prompt is public
    if (
      prompt.PromptTypeNo === PromptTypeNo.PUBLIC &&
      (!prompt.AuthorName.trim() || !prompt.AuthorURL.trim())
    ) {
      errors.push(
        'Please identify with Author Name and URL to publish a prompt template as public.'
      );
    }

    const missingPlaceholders = [];

    // require usage of target language placeholder if prompt is public
    if (
      prompt.PromptTypeNo === PromptTypeNo.PUBLIC &&
      !prompt.Prompt.includes(TargetLanguagePlaceholder)
    ) {
      missingPlaceholders.push(TargetLanguagePlaceholder);
    }

    // require usage of prompt placeholder in prompt template
    if (!prompt.Prompt.includes(PromptPlaceholder)) {
      missingPlaceholders.push(PromptPlaceholder);
    }

    // there is at least one missing placeholder
    if (missingPlaceholders.length > 0) {
      errors.push(
        `
          Make sure you follow the Prompt Template guidelines. <br>
          You must use ${missingPlaceholders.join(' and ')} correctly. <br><br>
          Learn more <a class="underline" href="https://lrt.li/aiprmpromptguide" target="_blank" rel="noopener noreferrer">here</a>.
        `
      );
    }

    // show error notification if there are any errors
    if (errors.length > 0) {
      const errorMessage = /*html*/ `
        <div>
          <strong>Please fix the following errors:</strong> <br><br>
          ${errors.join('<br><br>')}
        </div>
      `;

      this.showNotification(NotificationSeverity.ERROR, errorMessage, false);
    }

    return errors.length === 0;
  },

  // save prompt template via API and update client state
  async savePromptAsTemplate(e) {
    e.preventDefault();

    /** @type Prompt */
    const prompt = {};
    const formData = new FormData(e.target);

    for (const [key, value] of formData) {
      prompt[key] = value;
    }

    prompt.PromptTypeNo = prompt.Public
      ? PromptTypeNo.PUBLIC
      : PromptTypeNo.PRIVATE;

    // re-check user status
    await this.Client.checkUserStatus();

    if (!this.validatePrompt(prompt)) {
      return;
    }

    try {
      const savedPrompt = await this.Client.savePrompt(prompt);

      // Update revision time to current time
      prompt.RevisionTime = new Date().toISOString();

      // Update existing prompt template
      if (prompt.ID) {
        this.updatePromptsState(prompt);
      }
      // Add new prompt template to client state if it belongs to the current topic
      else if (
        this.PromptTopic === DefaultPromptTopic ||
        prompt.Community === this.PromptTopic
      ) {
        // New prompt template was created, set the ID
        prompt.ID = savedPrompt.ID;

        this.OwnPrompts.push(prompt);

        // Add prompt to public prompt templates if it is public
        if (prompt.Public) {
          this.PromptTemplates.push(prompt);
        }
      }
    } catch (error) {
      this.showNotification(
        NotificationSeverity.ERROR,
        error instanceof Reaction
          ? error.message
          : 'Something went wrong. Please try again.'
      );
      return;
    }

    this.hideSavePromptModal();

    this.showNotification(
      NotificationSeverity.SUCCESS,
      'Prompt template was saved successfully to "Own Prompts".'
    );

    this.insertPromptTemplatesSection();
  },

  /**
   * Update prompt templates in client state
   *
   * @param {Prompt} prompt
   */
  updatePromptsState(prompt) {
    // if topic doesn't match, remove prompt from PromptTemplates and OwnPrompts
    if (
      prompt.Community !== this.PromptTopic &&
      this.PromptTopic !== DefaultPromptTopic
    ) {
      this.PromptTemplates = this.PromptTemplates.filter(
        (template) => template.ID !== prompt.ID
      );

      this.OwnPrompts = this.OwnPrompts.filter(
        (ownPrompt) => ownPrompt.ID !== prompt.ID
      );

      return;
    }

    // find prompt in OwnPrompts by ID and update it
    this.OwnPrompts = this.OwnPrompts.map((ownPrompt) =>
      ownPrompt.ID === prompt.ID ? prompt : ownPrompt
    );

    // find the prompt in PromptTemplates by ID
    const promptTemplate = this.PromptTemplates.find(
      (template) => template.ID === prompt.ID
    );

    const isPublicPrompt = prompt.PromptTypeNo === PromptTypeNo.PUBLIC;

    // if prompt is not public and it is in PromptTemplates, remove it
    if (!isPublicPrompt && promptTemplate) {
      this.PromptTemplates = this.PromptTemplates.filter(
        (template) => template.ID !== prompt.ID
      );

      return;
    }

    // if prompt is public and it is not in PromptTemplates, add it
    if (isPublicPrompt && !promptTemplate) {
      this.PromptTemplates.push(prompt);

      return;
    }

    // if prompt is public and it is in PromptTemplates, update it
    if (isPublicPrompt && promptTemplate) {
      this.PromptTemplates = this.PromptTemplates.map((template) =>
        template.ID === prompt.ID ? prompt : template
      );
    }
  },

  /**
   * Simple notification based on ChatGPT "high demand" notification
   *
   * @param {NotificationSeverity} severity
   * @param {string} message
   * @param {boolean} autoHide
   */
  showNotification(
    severity = NotificationSeverity.SUCCESS,
    message = '',
    autoHide = true
  ) {
    const notificationElementID = 'AIPRM-Notification';

    let notificationElement = document.getElementById(notificationElementID);

    // if notification doesn't exist, create it
    if (!notificationElement) {
      notificationElement = document.createElement('div');
      notificationElement.id = notificationElementID;
    }

    const severityClassName = {
      [NotificationSeverity.SUCCESS]: 'bg-green-500',
      [NotificationSeverity.WARNING]: 'bg-orange-500',
      [NotificationSeverity.ERROR]: 'bg-red-500',
    };

    notificationElement.innerHTML = /*html*/ `
      <div class="fixed flex justify-center w-full top-2 px-2 z-50 pointer-events-none">
        <div class="${
          severityClassName[severity]
        } flex flex-row inline-flex pointer-events-auto px-6 py-3 rounded-md text-white" role="alert">
          <div class="flex gap-4">
            <p class="max-w-md">${message}</p>
            <button>${svg('Cross')}</button>
          </div>
        </div>
      </div>
    `;

    // remove notificationElement from DOM on click
    notificationElement
      .querySelector('button')
      .addEventListener('click', () => {
        notificationElement.remove();
      });

    // or remove notificationElement from DOM after 5 seconds
    if (autoHide) {
      setTimeout(() => {
        notificationElement.remove();
      }, 5000);
    }

    document.body.appendChild(notificationElement);
  },

  hideModal,

  hideSavePromptModal() {
    this.hideModal('savePromptModal');
  },

  // show modal to report prompt
  showReportPromptModal(PromptIndex) {
    createReportPromptModal(
      PromptIndex,
      this.PromptTemplatesType,
      this.PromptTemplates,
      this.reportPrompt.bind(this)
    );
  },

  /**
   * Show modal to save prompt as template
   *
   * @param {Event|null} e
   */
  async showSavePromptModal(e) {
    let promptTemplate = '';

    const isEditPromptEvent = e && e.type === editPromptTemplateEvent;

    // re-check user status in case it's not editing of existing prompt template
    if (!isEditPromptEvent) {
      await this.Client.checkUserStatus();
    }

    // cannot add new prompt template, but still can edit existing one
    if (!this.canCreatePromptTemplate() && !isEditPromptEvent) {
      this.cannotCreatePromptTemplateError();

      return;
    }

    // get the prompt template from current chat log if showSavePromptModal was called from "Save prompt as template" button (with event)
    if (e && e.type !== editPromptTemplateEvent) {
      // get the element that triggered this onclick event
      const button = e.target.closest('button');

      // get the parent element of the button (the prompt container)
      const prompt =
        button.parentElement.parentElement.parentElement.querySelector(
          '.whitespace-pre-wrap'
        );

      if (prompt) {
        promptTemplate = prompt.textContent;
      }
    }

    let savePromptModal = document.getElementById('savePromptModal');

    // if modal does not exist, create it, add event listener on submit and append it to body
    if (!savePromptModal) {
      savePromptModal = document.createElement('div');
      savePromptModal.id = 'savePromptModal';

      savePromptModal.addEventListener(
        'submit',
        this.savePromptAsTemplate.bind(this)
      );

      document.body.appendChild(savePromptModal);
    }

    savePromptModal.innerHTML = /*html*/ `
      <div class="fixed inset-0 text-center transition-opacity z-50">
        <div class="absolute bg-gray-900 inset-0 opacity-90">
        </div>

        <div class="fixed inset-0 overflow-y-auto">
          <div class="flex items-center justify-center min-h-full">
            <form id="savePromptForm">
              <input type="hidden" name="ID"  />
              <input type="hidden" name="OwnPrompt" value="true" />         
              <input type="hidden" name="Views" value="0" />
              <input type="hidden" name="Usages" value="0" />
              <input type="hidden" name="Votes" value="0" />
              
              <div
              class="align-center bg-white dark:bg-gray-800 dark:text-gray-200 inline-block overflow-hidden sm:rounded-lg shadow-xl sm:align-middle sm:max-w-lg sm:my-8 sm:w-full text-left transform transition-all"
              role="dialog" aria-modal="true" aria-labelledby="modal-headline" style="text-align: left;">
          
                <div class="bg-white dark:bg-gray-800 px-4 pt-5 pb-4 sm:p-6 sm:pb-4 overflow-y-auto">
                  <label>Prompt Template</label>
                  <textarea name="Prompt" class="w-full bg-gray-100 dark:bg-gray-700 dark:border-gray-700 rounded p-2 mt-2 mb-3" style="height: 120px;" required
                            placeholder="Prompt text including placeholders [TARGETLANGUAGE] or [PROMPT] replaced automagically by AIPRM"
                            title="Prompt text including placeholders like [TARGETLANGUAGE] or [PROMPT] replaced automagically by AIPRM">${sanitizeInput(
                              promptTemplate
                            )}</textarea>
            
                  <label>Teaser</label>
                  <textarea name="Teaser" required
                    title="Short teaser for this prompt template, e.g. 'Create a keyword strategy and SEO content plan from 1 [KEYWORD]'"
                    class="w-full bg-gray-100 dark:bg-gray-700 dark:border-gray-700 rounded p-2 mt-2 mb-3" style="height: 71px;"
                    placeholder="Create a keyword strategy and SEO content plan from 1 [KEYWORD]"></textarea>
                    
                  <label>Prompt Hint</label>
                  <input name="PromptHint" required type="text"
                    title="Prompt hint for this prompt template, e.g. '[KEYWORD]' or '[your list of keywords, maximum ca. 8000]"
                    class="w-full bg-gray-100 dark:bg-gray-700 dark:border-gray-700 rounded p-2 mt-2 mb-3" placeholder="[KEYWORD] or [your list of keywords, maximum ca. 8000]" />

                  <label>Title</label>
                  <input name="Title" type="text" 
                    title="Short title for this prompt template, e.g. 'Keyword Strategy'" required placeholder="Keyword Strategy" class="w-full bg-gray-100 dark:bg-gray-700 dark:border-gray-700 rounded mb-3 mt-2 p-2 w-full" />
            
                  <div class="flex">
                    <div class="mr-4 w-full">
                      <label>Topic</label>
                      <select name="Community" class="mt-2 mb-3 dark:bg-gray-700 dark:border-gray-700 dark:hover:bg-gray-900 rounded w-full" required>
                        ${this.Topics.map(
                          (topic) => /*html*/ `
                              <option value="${sanitizeInput(topic.ID)}" ${
                            topic.ID === this.PromptTopic ? 'selected' : ''
                          }>${sanitizeInput(topic.Label)}</option>`
                        ).join('')}
                      </select>
                    </div>

                    <div class="w-full">
                      <label>Activity</label>
                      <select name="Category" class="mt-2 mb-3 dark:bg-gray-700 dark:border-gray-700 dark:hover:bg-gray-900 rounded w-full" required>
                        ${this.getActivities(
                          this.PromptTopic === DefaultPromptTopic
                            ? this.Topics[0].ID
                            : this.PromptTopic
                        )
                          .map(
                            (activity) => /*html*/ `
                              <option value="${sanitizeInput(
                                activity.ID
                              )}">${sanitizeInput(activity.Label)}</option>`
                          )
                          .join('')}
                      </select>
                    </div>
                  </div>

                  <div class="block mt-4">
                    <label class="text-sm">
                      <input name="Public" value="true" type="checkbox" class="mr-2 dark:bg-gray-700"> 
                      Share prompt template publicly
                    </label>
                    
                    <div class="flex justify-between mt-4">
                      <div class="mr-4 w-full"><label>Author Name</label>
                        <input name="AuthorName" type="text" title="Author Name visible for all users"
                              placeholder="Author Name" class="bg-gray-100 dark:bg-gray-700 dark:border-gray-700 rounded mb-3 mt-2 p-2 w-full" />
                      </div>

                      <div class="w-full"><label>Author URL</label>
                        <input name="AuthorURL" type="url" title="Author URL visible for all users"
                              placeholder="https://www.example.com/" class="bg-gray-100 dark:bg-gray-700 dark:border-gray-700 rounded mb-3 mt-2 p-2 w-full" />
                      </div>
                    </div>                
                  </div>
            
                  <p class="mt-6 text-[10px]">Please be mindful of what you share, and do not include any confidential information, as we are not responsible for
                    any actions taken by others with the information you choose to share.</p>
                </div>
            
                <div class="bg-gray-200 dark:bg-gray-700 px-4 py-3 text-right">
                  <button type="button" class="bg-gray-600 hover:bg-gray-800 mr-2 px-4 py-2 rounded text-white"
                          onclick="AIPRM.hideSavePromptModal()"> Cancel
                  </button>
                  <button type="submit" class="bg-green-600 hover:bg-green-700 mr-2 px-4 py-2 rounded text-white">Save Prompt
                  </button>
                </div>
            
              </div>
            </form>
          </div>
        </div>
        
      </div>
    `;

    // add onchange event listener to select[name="Community"] to update the activities
    savePromptModal.querySelector('select[name="Community"]').onchange = (
      event
    ) => {
      // replace select[name="Category"] with new activities
      savePromptModal.querySelector('select[name="Category"]').innerHTML =
        this.getActivities(event.target.value)
          .map(
            (activity) => /*html*/ `
            <option value="${sanitizeInput(activity.ID)}">${sanitizeInput(
              activity.Label
            )}</option>`
          )
          .join('');
    };

    savePromptModal.style = 'display: block;';

    // add event listener to close the modal on ESC
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.hideSavePromptModal();
      }
    });
  },

  // This function adds an "Export Button" to the sidebar
  addExportButton() {
    // Get the nav element in the sidebar
    const nav = document.querySelector('nav');
    // If there is no nav element or the "Export Button" already exists, skip
    if (!nav || nav.querySelector('#export-button')) return;

    // Create the "Export Button" element
    const button = document.createElement('a');
    button.id = 'export-button';
    button.className = css`ExportButton`;
    button.innerHTML = /*html*/ `${svg`Export`} Export Chat`;
    button.onclick = this.exportCurrentChat.bind(this);

    // If there is no chat started, disable the button
    if (document.querySelector('.flex-1.overflow-hidden h1')) {
      button.style = 'pointer-events: none;opacity: 0.5';
    }

    // Get the Log out button as a reference
    const colorModeButton = [...nav.children].find((child) =>
      child.innerText.includes('Log out')
    );
    // Insert the "Export Button" before the "Color Mode" button
    nav.insertBefore(button, colorModeButton);

    // Create the "Version" element
    const version = document.createElement('a');
    version.id = 'AppName';
    version.className = css`VersionInfo`;
    version.innerHTML = /*html*/ `${svg`Rocket`}` + AppName + ' powered';
    //version.onclick = exportCurrentChat
    version.href = AppURL;

    // Get the Log out button as a reference
    const colorModeButton2 = [...nav.children].find((child) =>
      child.innerText.includes('Log out')
    );
    // Insert the "Export Button" before the "Color Mode" button

    nav.insertBefore(version, colorModeButton2);
  },

  // This function gets the "New Chat" buttons
  getNewChatButtons() {
    // Get the sidebar and topbar elements
    const sidebar = document.querySelector('nav');
    const topbar = document.querySelector('.sticky');
    // Get the "New Chat" button in the sidebar
    const newChatButton = [
      ...(sidebar?.querySelectorAll('.cursor-pointer') ?? []),
    ].find((e) => e.innerText === 'New chat');
    // Get the "Plus" button in the topbar
    const AddButton = topbar?.querySelector('button.px-3');
    // Return an array containing the buttons, filtering out any null elements
    return [newChatButton, AddButton].filter((button) => button);
  },

  // This function inserts a section containing a list of prompt templates into the chat interface
  insertPromptTemplatesSection() {
    // If there are no topics or activities do not insert the section, yet
    if (!this.Topics.length || !this.Activities.length) {
      return;
    }

    // Get the title element (as a reference point and also for some alteration)
    const title = document.querySelector('h1.text-4xl');
    // If there is no title element, return
    if (!title) return;

    // Hide the title element and examples
    title.style = 'display: none';

    // Hide the examples if they are present, but do not hide own templates wrapper
    if (title.nextSibling && title.nextSibling.id !== 'templates-wrapper') {
      title.nextSibling.style = 'display: none;';
    }

    // Get the list of prompt templates
    let templates = this.PromptTemplates;
    // If there are no templates, skip
    if (!templates) return;

    templates =
      this.PromptTemplatesType === PromptTemplatesType.OWN
        ? this.OwnPrompts
        : templates;

    // Use index as ID for each template actions
    templates = templates.map((template, index) => ({
      ...template,
      ID: index,
    }));

    // Filter templates based on selected activity and search query
    templates = templates.filter((template) => {
      return (
        (this.PromptActivity === DefaultPromptActivity ||
          template.Category === this.PromptActivity) &&
        (!this.PromptSearch ||
          template.Teaser.toLowerCase().includes(
            this.PromptSearch.toLowerCase()
          ) ||
          template.Title.toLowerCase().includes(
            this.PromptSearch.toLowerCase()
          ))
      );
    });

    // Get the parent element of the title element (main page)
    const parent = title.parentElement;
    // If there is no parent element, skip
    if (!parent) return;

    // Remove the "md:h-full" class from the parent element
    parent.classList.remove('md:h-full');

    // Get the current page number and page size from the promptTemplateSection object
    const { currentPage, pageSize } = this.PromptTemplateSection;
    // Calculate the start and end indices of the current page of prompt templates
    const start = pageSize * currentPage;
    const end = Math.min(pageSize * (currentPage + 1), templates.length);
    // Get the current page of prompt templates
    const currentTemplates = templates.slice(start, end);

    // Pagination buttons (conditionally rendered, depending on the number of prompt templates)
    const paginationContainer = /*html*/ `
    <div class="flex flex-1 gap-3.5 justify-between items-center sm:flex-col mt-6">
      <div class="text-left" style="margin-top: -1rem;">
        <label class="block text-sm font-medium" title="The number of prompt templates per page">Prompts per Page</label>
        <select class="bg-gray-100 border-0 text-sm rounded block w-full dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white hover:bg-gray-200 focus:ring-0 dark:hover:bg-gray-900 pageSizeSelect">
          ${pageSizeOptions
            .map(
              (pageSize) => /*html*/ `
                <option value="${pageSize}" ${
                pageSize === this.PromptTemplateSection.pageSize
                  ? 'selected'
                  : ''
              }>${pageSize}</option>`
            )
            .join('')}
        </select>
      </div>
      
      <span class="${css`paginationText`}">
        Showing <span class="${css`paginationNumber`}">${
      start + 1
    }</span> to <span class="${css`paginationNumber`}">${end}</span> of <span class="${css`paginationNumber`}">${
      templates.length
    } Prompts</span>
      </span>
      <div class="${css`paginationButtonGroup`}">
        <button onclick="AIPRM.prevPromptTemplatesPage()" class="${css`paginationButton`}" style="border-radius: 6px 0 0 6px">Prev</button>
        <button onclick="AIPRM.nextPromptTemplatesPage()" class="${css`paginationButton`} border-0 border-l border-gray-500" style="border-radius: 0 6px 6px 0">Next</button>
      </div>
    </div>
  `;

    // Create the HTML for the prompt templates section
    const html = /*html*/ `
    <div class="${css`column`} relative">

      ${
        this.isAdmin()
          ? /*html*/ `
            <div class="absolute top-0 right-0">
              <label class="relative inline-flex items-center mb-5 cursor-pointer flex-col" title="Admin Mode">
                <input type="checkbox" value="" class="sr-only peer" id="adminMode" onchange="AIPRM.toggleAdminMode()" ${
                  this.AdminMode ? ' checked' : ''
                }>
                <div class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all dark:border-gray-600 peer-checked:bg-gray-600"></div>
                <span class="ml-3 text-sm font-medium text-gray-900 dark:text-gray-300"></span>
              </label>
            </div>
          `
          : ''
      }
    
      ${svg`PromptBubble`}
      
      <h2 class="${css`h2`}"></h2>
      
      <ul class="border-b border-gray-200 dark:border-gray-700 dark:text-gray-400 flex flex-wrap font-medium text-center text-gray-500 text-sm">
        <li class="flex-1 mr-2">
          <a href="#" id="publicPromptsTab" onclick="AIPRM.changePromptTemplatesType('${
            PromptTemplatesType.PUBLIC
          }')" 
          class="${
            this.PromptTemplatesType === PromptTemplatesType.PUBLIC
              ? 'bg-gray-50 dark:bg-white/5'
              : ''
          } dark:hover:bg-gray-900 dark:hover:text-gray-300 hover:bg-gray-50 hover:text-gray-600 inline-block p-4 rounded-t-lg" style="width: 100%;">
            Public Prompts
          </a>
        </li>
        <li class="flex-1" style="width: 100%;">
          <a href="#" id="ownPromptsTab" onclick="AIPRM.changePromptTemplatesType('${
            PromptTemplatesType.OWN
          }')" 
          class="${
            this.PromptTemplatesType === PromptTemplatesType.OWN
              ? 'bg-gray-50 dark:bg-white/5'
              : ''
          } dark:hover:bg-gray-900 dark:hover:text-gray-300 hover:bg-gray-50 hover:text-gray-600 inline-block p-4 rounded-t-lg" style="width: 100%;">
            Own Prompts
          </a>
        </li>
      </ul>
  
      <div class="grid grid-cols-2 sm:flex flex-row gap-3 items-end justify-between lg:-mb-4 lg:max-w-3xl md:last:mb-6 pt-2 stretch text-left text-sm">
        <div>
          <label for="topicSelect" class="block text-sm font-medium">Topic</label>
      
          <select id="topicSelect" class="bg-gray-100 border-0 text-sm rounded block w-full dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white hover:bg-gray-200 focus:ring-0 dark:hover:bg-gray-900">
            <option value="${DefaultPromptTopic}" 
            ${
              this.PromptTopic === DefaultPromptTopic ? 'selected' : ''
            }>All</option>

            ${this.Topics.map(
              (topic) =>
                /*html*/ `<option value="${sanitizeInput(topic.ID)}" ${
                  this.PromptTopic === topic.ID ? 'selected' : ''
                }>${sanitizeInput(topic.Label)}</option>`
            ).join('')}
          </select>
        </div>

        <div>
          <label for="activitySelect" class="block text-sm font-medium">Activity</label>
      
          <select id="activitySelect" class="bg-gray-100 border-0 text-sm rounded block w-full dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white hover:bg-gray-200 focus:ring-0 dark:hover:bg-gray-900">
            <option value="${DefaultPromptActivity}" 
            ${
              this.PromptActivity === DefaultPromptActivity ? 'selected' : ''
            }>All</option>

            ${this.getActivities(this.PromptTopic)
              .map(
                (activity) =>
                  /*html*/ `<option value="${sanitizeInput(activity.ID)}" ${
                    this.PromptActivity === activity.ID ? 'selected' : ''
                  }>${sanitizeInput(activity.Label)}</option>`
              )
              .join('')}
          </select>
        </div>

        <div>
          <label for="sortBySelect" class="block text-sm font-medium">Sort by</label>
      
          <select id="sortBySelect" class="bg-gray-100 border-0 text-sm rounded block w-full dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white hover:bg-gray-200 focus:ring-0 dark:hover:bg-gray-900">
            ${Object.keys(SortModeNo)
              .map(
                (sortMode) => /*html*/ `
                <option value="${SortModeNo[sortMode]}" ${
                  this.PromptSortMode === SortModeNo[sortMode] ? 'selected' : ''
                }>${capitalizeWords(sortMode.replace('_', ' '))}</option>`
              )
              .join('')}
          </select>
        </div>
        
        <div>
          <input id="promptSearchInput" type="text" class="bg-gray-100 border-0 text-sm rounded block w-full dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white hover:bg-gray-200 focus:ring-0 md:w-[260px]" placeholder="Search" 
          value="${sanitizeInput(
            this.PromptSearch
          )}" onfocus="this.value = this.value">
        </div>
      </div>

      ${
        templates.length > this.PromptTemplateSection.pageSize
          ? paginationContainer
          : ''
      }
      
      <ul class="${css`ul`} grid grid-cols-1 lg:grid-cols-2">
        ${currentTemplates
          .map(
            (template) => /*html*/ `
          <button onclick="AIPRM.selectPromptTemplateByIndex(${
            template.ID
          })" class="${css`card`} relative group">
            <div class="flex items-start w-full justify-between">
              <h3 class="${css`h3`}" style="overflow-wrap: anywhere;">${sanitizeInput(
              template.Title
            )}</h3>

              <div class="flex gap-4 justify-center lg:gap-1 lg:pl-2 mt-1 right-2 text-gray-400 lg:invisible group-hover:visible">

                ${
                  this.PromptTemplatesType === PromptTemplatesType.PUBLIC &&
                  !template.OwnPrompt
                    ? /*html*/ `
                      <a title="Vote for this prompt with thumbs up" class="p-1 rounded-md hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-200 disabled:dark:hover:text-gray-400" onclick="event.stopPropagation(); AIPRM.voteThumbsUp(${
                        template.ID
                      })">${svg('ThumbUp')}</a>
                  
                      <a title="Vote for this prompt with thumbs down" class="p-1 rounded-md hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-200 disabled:dark:hover:text-gray-400" onclick="event.stopPropagation(); AIPRM.voteThumbsDown(${
                        template.ID
                      })">${svg('ThumbDown')}</a>
                      
                      <a title="Report this prompt" class="p-1 rounded-md hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-200 disabled:dark:hover:text-gray-400" onclick="event.stopPropagation(); AIPRM.showReportPromptModal(${
                        template.ID
                      })">${svg('Report')}</a>
                    `
                    : ''
                }
                
                ${
                  this.PromptTemplatesType === PromptTemplatesType.OWN ||
                  template.OwnPrompt ||
                  this.isAdminMode()
                    ? /*html*/ `
                  <a title="Edit this prompt" class="p-1 rounded-md hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-200 disabled:dark:hover:text-gray-400" onclick="event.stopPropagation(); AIPRM.editPromptTemplate(${
                    template.ID
                  })">${svg('Edit')}</a>
                  <a title="Delete this prompt" class="p-1 rounded-md hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-200 disabled:dark:hover:text-gray-400" onclick="event.stopPropagation(); AIPRM.deletePromptTemplate(${
                    template.ID
                  })">${svg('Cross')}</a>
                  `
                    : ''
                }
              </div>
            </div>      

            <div class="-mt-0.5 text-gray-500 text-xs pb-1 max-w-full">
              <span title="Topic: ${sanitizeInput(
                this.getTopicLabel(template.Community)
              )}">
                ${sanitizeInput(this.getTopicLabel(template.Community))}
              </span>
              / 
              <span title="Activity: ${sanitizeInput(
                this.getActivityLabel(template.Category)
              )}">
                ${sanitizeInput(this.getActivityLabel(template.Category))}
              </span>
            </div>

            <div class="text-gray-500 text-xs flex pb-1 max-w-full">
              ${
                template.PromptTypeNo === PromptTypeNo.PUBLIC
                  ? /*html*/ `<span class="mr-1" title="Public">${svg(
                      'Globe'
                    )}</span>`
                  : /*html*/ `<span class="mr-1" title="Private">${svg(
                      'Lock'
                    )}</span>`
              }

              ${
                template.AuthorURL && template.AuthorName
                  ? /*html*/ `· 
                    <a href="${sanitizeInput(
                      template.AuthorURL
                    )}" class="mx-1 underline overflow-hidden text-ellipsis flex-1"
                      style="white-space: nowrap;"
                      onclick="event.stopPropagation()"
                      rel="noopener noreferrer" target="_blank"
                      title="Created by ${sanitizeInput(template.AuthorName)}">
                      ${sanitizeInput(template.AuthorName)}
                    </a>`
                  : ''
              }            
              · 
              <span title="Last updated on ${formatDateTime(
                template.RevisionTime
              )}" class="mx-1">${formatAgo(template.RevisionTime)}</span>
            </div>
            
            <p class="${css`p`} text-gray-600 dark:text-gray-200 overflow-hidden text-ellipsis" style="display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;"
              title="${sanitizeInput(template.Teaser)}">
              ${sanitizeInput(template.Teaser)}
            </p>

          <div class="text-gray-500 text-xs flex pt-3 w-full justify-between" style="margin-top: auto;">
              <span class="flex items-center" title="Views (${template.Views})">
                <span class="p-1">${svg(
                  'Eye'
                )}</span> &nbsp; ${formatHumanReadableNumber(template.Views)}
              </span>

              <span class="flex items-center" title="Usages (${
                template.Usages
              })">
                <span class="p-1">${svg(
                  'Quote'
                )}</span> &nbsp; ${formatHumanReadableNumber(template.Usages)}
              </span>

              <span class="flex items-center" title="Votes (${template.Votes})">
                ${
                  !template.OwnPrompt
                    ? /*html*/ `<a title="Votes (${
                        template.Votes
                      }) - Vote for this prompt with thumbs up"
                      class="p-1 rounded-md hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-200 disabled:dark:hover:text-gray-400" onclick="event.stopPropagation(); AIPRM.voteThumbsUp(${
                        template.ID
                      })">${svg('ThumbUp')}</a>`
                    : /*html*/ `${svg('ThumbUp')}`
                }
                &nbsp; ${formatHumanReadableNumber(template.Votes)}
              </span>

              <span class="flex items-center" title="Copy link to this prompt">
                <a class="p-1 rounded-md hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-200 disabled:dark:hover:text-gray-400" 
                onclick="event.stopPropagation(); AIPRM.copyPromptDeepLink(${
                  template.ID
                })" title="Copy link to this prompt">
                ${svg('Link')}
                </a>
              </span>
          </div>
          
        </button>
      `
          )
          .join('')}
            
        ${
          this.PromptTemplatesType === PromptTemplatesType.OWN
            ? /*html*/ `<button onclick="AIPRM.showSavePromptModal()" class="${css`card`} relative group justify-center items-center ${
                !this.canCreatePromptTemplate()
                  ? 'text-gray-300 cursor-not-allowed dark:hover:bg-gray-500/10'
                  : ''
              }">
            <div class="flex items-center gap-3">
              ${svg('Plus')}
              Add new prompt template   
            </div>
          </button>`
            : ''
        }
      </ul>
    
      ${
        templates.length > this.PromptTemplateSection.pageSize
          ? paginationContainer
          : ''
      }
      
    </div>
   `;

    let wrapper = document.createElement('div');
    wrapper.id = 'templates-wrapper';
    wrapper.className =
      'mt-6 md:flex items-start text-center gap-2.5 md:max-w-2xl lg:max-w-3xl m-auto text-sm';

    if (parent.querySelector('#templates-wrapper')) {
      wrapper = parent.querySelector('#templates-wrapper');
    } else {
      parent.appendChild(wrapper);
    }

    wrapper.innerHTML = html;

    // Add event listeners for topic, activity, sort by select, search input and prompts per page select
    wrapper
      .querySelector('#topicSelect')
      .addEventListener('change', this.changePromptTopic.bind(this));

    wrapper
      .querySelector('#activitySelect')
      .addEventListener('change', this.changePromptActivity.bind(this));

    wrapper
      .querySelector('#sortBySelect')
      .addEventListener('change', this.changePromptSortBy.bind(this));

    wrapper
      .querySelector('#promptSearchInput')
      .addEventListener(
        'input',
        this.debounce(this.changePromptSearch.bind(this), 300).bind(this)
      );

    const pageSizeSelectElements = wrapper.querySelectorAll(
      'select.pageSizeSelect'
    );

    // Remove event listener for the pagination buttons (if not needed/already added)
    document.removeEventListener('keydown', this.boundHandleArrowKey);

    // Add event listener for the pagination buttons and page size select elements
    if (pageSizeSelectElements.length > 0) {
      pageSizeSelectElements.forEach((select) => {
        select.addEventListener('change', this.changePromptPageSize.bind(this));
      });

      // Add event listener for the pagination buttons
      document.addEventListener('keydown', this.boundHandleArrowKey);
    }
  },

  /**
   * boundHandleArrowKey is the bound version of the handleArrowKey function
   *
   * @type {function(e: KeyboardEvent): void}
   */
  boundHandleArrowKey: null,

  // handleArrowKey handles the arrow key presses for the page navigation
  handleArrowKey(e) {
    const isArrowKey = e.key === 'ArrowLeft' || e.key === 'ArrowRight';

    const isInput =
      e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA';

    if (!isArrowKey || isInput) {
      // If the key pressed is not an arrow key or if it was pressed in an input or textarea element, do nothing
      return;
    }

    // If the key pressed is a left arrow key, call the previous page function
    if (e.key === 'ArrowLeft') {
      this.prevPromptTemplatesPage();

      return;
    }

    // Otherwise, call the next page function
    this.nextPromptTemplatesPage();
  },

  // changePromptPageSize updates the this.PromptTemplateSection.pageSize variable and re-renders the templates
  changePromptPageSize(e) {
    let pageSize = +e.target.value;

    // if the pageSize is not in the pageSizeOptions array, use the default pageSize option
    pageSize = pageSizeOptions.includes(pageSize) ? pageSize : pageSizeDefault;

    // persist the last selected page size in local storage
    localStorage.setItem(lastPageSizeKey, pageSize);

    this.PromptTemplateSection.currentPage = 0;
    this.PromptTemplateSection.pageSize = pageSize;

    this.insertPromptTemplatesSection();
  },

  // changePromptTopic updates the this.PromptTopic variable and reloads the templates & messages
  changePromptTopic(e) {
    this.PromptTopic = e.target.value;

    this.PromptActivity = DefaultPromptActivity;

    this.PromptTemplateSection.currentPage = 0;

    this.selectPromptTemplateByIndex(null);

    // persist the last selected topic in local storage
    localStorage.setItem(lastPromptTopicKey, this.PromptTopic);

    this.fetchPromptTemplates();

    this.fetchMessages();
  },

  // changePromptActivity updates the this.PromptActivity variable and re-renders the templates
  changePromptActivity(e) {
    this.PromptActivity = e.target.value;

    this.PromptTemplateSection.currentPage = 0;

    this.insertPromptTemplatesSection();
  },

  // changePromptSortBy updates the this.PromptSortMode variable and reloads the templates
  changePromptSortBy(e) {
    this.PromptSortMode = +e.target.value;

    this.PromptTemplateSection.currentPage = 0;

    this.fetchPromptTemplates();
  },

  // changePromptSearch updates the this.PromptSearch variable and re-renders the templates
  changePromptSearch(e) {
    this.PromptSearch = e.target.value;

    this.PromptTemplateSection.currentPage = 0;

    this.insertPromptTemplatesSection();

    const searchInput = document.querySelector('#promptSearchInput');

    searchInput.selectionStart = searchInput.selectionEnd =
      searchInput.value.length;
    searchInput.focus();
  },
  /**
   * changePromptTemplatesType updates the this.PromptTemplatesType variable and re-renders the templates
   *
   * @param {PromptTemplatesType} type
   */
  changePromptTemplatesType(type) {
    if (this.PromptTemplatesType === type) {
      return;
    }

    this.PromptTemplatesType = type;

    this.PromptTemplateSection.currentPage = 0;

    this.insertPromptTemplatesSection();
  },

  // debounce is a function that returns a function that will only execute after a certain amount of time has passed
  debounce(callback, milliseconds) {
    let timeout;

    return (argument) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => callback(argument), milliseconds);
    };
  },

  // Insert language select and continue button above the prompt textarea input
  insertLanguageToneWritingStyleContinueActions() {
    let wrapper = document.createElement('div');

    wrapper.id = 'language-select-wrapper';
    wrapper.className = css('languageSelectWrapper');

    // Get the list of languages
    const languages = this.Languages;

    // If there are no languages, skip
    if (!languages) return;

    // Get the prompt textarea input
    const textarea = document.querySelector('form textarea');

    // If there is no textarea, skip
    if (!textarea) return;

    // Hide the spacer for absolutely positioned prompt input
    const spacer = document.querySelector(
      '.w-full.h-32.md\\:h-48.flex-shrink-0'
    );

    if (spacer) {
      spacer.style = 'display: none';
    }

    // Remove the absolute positioning from the prompt input parent
    const formParent = textarea.form.parentElement;

    if (formParent) {
      formParent.classList.remove(
        'absolute',
        'md:!bg-transparent',
        'md:border-t-0',
        'md:dark:border-transparent',
        'md:border-transparent'
      );
    }

    // Get the parent of the textarea
    const parent = textarea.parentElement;

    // If there is no parent element, skip
    if (!parent) return;

    // Add padding to the parent element
    parent.classList.add('pr-4');

    // Get existing language select wrapper or create a new one
    if (parent.querySelector(`#${wrapper.id}`)) {
      wrapper = parent.querySelector(`#${wrapper.id}`);
    } else {
      parent.prepend(wrapper);
    }

    // Create the HTML for the language select section
    wrapper.innerHTML = /*html*/ `
    <div class="flex w-full">
      <div>
        <label for="languageSelect" class="${css(
          'selectLabel'
        )}" style="white-space: nowrap;">Output in</label>
        
        <select id="languageSelect" class="${css('select')}">
          <option value ${
            !this.TargetLanguage ? ' selected' : ''
          }>Default language</option>  

          ${this.Languages.map(
            (language) => `
            <option value="${language.languageEnglish}" ${
              this.TargetLanguage === language.languageEnglish
                ? ' selected'
                : ''
            }>
              ${language.languageLabel}
              </option> 
          `
          ).join('')}
        </select>
      </div>
      
      <div class="ml-2">
        <label for="toneSelect" class="${css('selectLabel')}">Tone</label>
      
        <select id="toneSelect" class="${css('select')}">
          <option value ${!this.Tone ? ' selected' : ''}>Default</option>

          ${this.Tones.map(
            (tone) => `
            <option value="${tone.ID}" ${
              this.Tone === tone.ID ? ' selected' : ''
            }>
              ${tone.Label}
              </option> 
          `
          ).join('')}
        </select>
      </div>

      <div class="ml-2">
        <label for="writingStyleSelect" class="${css(
          'selectLabel'
        )}" style="white-space: nowrap;">Writing Style</label>
      
        <select id="writingStyleSelect" class="${css('select')}">
          <option value ${
            !this.WritingStyle ? ' selected' : ''
          }>Default</option>

          ${this.WritingStyles.map(
            (writingStyle) => `
            <option value="${writingStyle.ID}" ${
              this.WritingStyle === writingStyle.ID ? ' selected' : ''
            }>
              ${writingStyle.Label}
              </option> 
          `
          ).join('')}
        </select>
      </div>
    </div>

    <div class="inline-flex invisible" role="group" id="continueActionsGroup">
      <button id="continueWritingButton" title="Continue writing please" class="${css(
        'continueButton'
      )}" onclick="event.stopPropagation(); AIPRM.continueWriting()" type="button">
        Continue
      </button>

      <select id="continueActionSelect" class="${css('continueActionSelect')}">
        <option value selected disabled>-- Select an action --</option>

        ${this.ContinueActions.map(
          (action) => `
          <option value="${action.ID}">${action.Label}</option>
        `
        ).join('')}
      </select>
    </div>
  `;

    // Add event listener to language select to update the target language on change
    wrapper
      .querySelector('#languageSelect')
      .addEventListener('change', this.changeTargetLanguage.bind(this));

    // Add event listener to tone select to update the tone on change
    wrapper
      .querySelector('#toneSelect')
      .addEventListener('change', this.changeTone.bind(this));

    // Add event listener to writing style select to update the writing style on change
    wrapper
      .querySelector('#writingStyleSelect')
      .addEventListener('change', this.changeWritingStyle.bind(this));

    // Add event listener to continue action select to update the continue action on change
    wrapper
      .querySelector('#continueActionSelect')
      .addEventListener('change', this.changeContinueAction.bind(this));
  },

  // Change the TargetLanguage on selection change
  changeTargetLanguage(event) {
    this.TargetLanguage = event.target.value;

    // persist the last selected language in local storage
    localStorage.setItem(lastTargetLanguageKey, this.TargetLanguage);
  },

  // Change the Tone on selection change
  changeTone(event) {
    this.Tone = parseInt(event.target.value);
  },

  // Change the WritingStyle on selection change
  changeWritingStyle(event) {
    this.WritingStyle = parseInt(event.target.value);
  },

  // Change the ContinueAction on selection change and submit the continue action prompt
  changeContinueAction(event) {
    const continueActionID = parseInt(event.target.value);

    // Get prompt for the selected continue action
    const continueAction = this.ContinueActions.find(
      (action) => action.ID === continueActionID
    );

    // If the continue action is not found, skip
    if (!continueAction) {
      return;
    }

    // Track usage of continue action
    this.Client.usePrompt(`${continueAction.ID}`, UsageTypeNo.SEND);

    // Submit the continue action prompt
    this.submitContinueActionPrompt(continueAction.Prompt);
  },

  // Ask ChatGPT to continue writing
  continueWriting() {
    this.submitContinueActionPrompt('Continue writing please');
  },

  // Submit the continue action prompt to ChatGPT
  submitContinueActionPrompt(prompt = '') {
    const textarea = document.querySelector('form textarea');

    // If the textarea is not empty and it's not "Continue writing please" - ask for confirmation
    if (
      textarea.value.trim() &&
      textarea.value.trim() !== 'Continue writing please' &&
      !confirm(
        'Are you sure you want to continue? The current prompt text will be lost.'
      )
    ) {
      return;
    }

    // Add the continue action prompt to the textarea
    textarea.value = prompt;
    textarea.focus();

    // select button element which is in form and it's direct next sibling of textarea
    let button = textarea.nextElementSibling;

    // If the button is not found, skip
    if (
      !button ||
      !button.tagName ||
      button.tagName.toLowerCase() !== 'button'
    ) {
      return;
    }

    // Click the "Submit" button
    button.click();
  },

  hideContinueActionsButton() {
    const button = document.querySelector('#continueActionsGroup');

    if (!button) {
      return;
    }

    button.classList.add('invisible');
  },

  showContinueActionsButton() {
    const button = document.querySelector('#continueActionsGroup');

    if (!button) {
      return;
    }

    button.classList.remove('invisible');
  },

  // Decrement the current page of the prompt templates section and re-render
  prevPromptTemplatesPage() {
    this.PromptTemplateSection.currentPage--;
    this.PromptTemplateSection.currentPage = Math.max(
      0,
      this.PromptTemplateSection.currentPage
    );

    // Update the section
    this.insertPromptTemplatesSection();
  },

  // nextPromptTemplatesPage increments the current page and re-renders the templates
  nextPromptTemplatesPage() {
    const templates =
      this.PromptTemplatesType === PromptTemplatesType.OWN
        ? this.OwnPrompts
        : this.PromptTemplates;

    if (!templates || !Array.isArray(templates)) return;

    this.PromptTemplateSection.currentPage++;
    this.PromptTemplateSection.currentPage = Math.min(
      Math.floor((templates.length - 1) / this.PromptTemplateSection.pageSize),
      this.PromptTemplateSection.currentPage
    );

    // Update the section
    this.insertPromptTemplatesSection();
  },

  // Export the current chat log to a file
  exportCurrentChat() {
    const blocks = [
      ...document.querySelector('.flex.flex-col.items-center').children,
    ];

    let markdown = blocks.map((block) => {
      let wrapper = block.querySelector('.whitespace-pre-wrap');

      if (!wrapper) {
        return '';
      }

      // probably a user's, so..
      if (wrapper.children.length === 0) {
        return '**User:**\n' + wrapper.innerText;
      }

      // pass this point is assistant's

      wrapper = wrapper.firstChild;

      return (
        '**ChatGPT:**\n' +
        [...wrapper.children]
          .map((node) => {
            switch (node.nodeName) {
              case 'PRE':
                return `\`\`\`${
                  node
                    .getElementsByTagName('code')[0]
                    .classList[2].split('-')[1]
                }\n${node.innerText.replace(/^Copy code/g, '').trim()}\n\`\`\``;
              default:
                return `${node.innerHTML}`;
            }
          })
          .join('\n')
      );
    });

    markdown = markdown.filter((b) => b);

    if (!markdown) return false;

    let header = '';

    try {
      header =
        ExportHeaderPrefix +
        window.__NEXT_DATA__.props.pageProps.user.name +
        ' on ' +
        new Date().toLocaleString() +
        '\n```\n\n---';
    } catch {
      console.error(
        'Failed to get user name from window.__NEXT_DATA__.props.pageProps.user.name. Using default header instead.'
      );
    }

    const blob = new Blob([header + '\n\n\n' + markdown.join('\n\n---\n\n')], {
      type: 'text/plain',
    });

    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    //a.download = 'chatgpt-thread_' + (new Date().toLocaleString('en-US', { hour12: false }).replace(/[\s/:]/g, '-').replace(',', '')) + '.md'
    a.download = ExportFilePrefix + new Date().toISOString() + '.md';
    document.body.appendChild(a);
    a.click();
  },

  // Edit the prompt template
  async editPromptTemplate(idx) {
    const prompt =
      this.PromptTemplatesType === PromptTemplatesType.OWN
        ? this.OwnPrompts[idx]
        : this.PromptTemplates[idx];

    // Only allow editing of own prompt templates
    if (
      this.PromptTemplatesType !== PromptTemplatesType.OWN &&
      !prompt.OwnPrompt &&
      !this.isAdminMode()
    ) {
      return;
    }

    await this.showSavePromptModal(new CustomEvent(editPromptTemplateEvent));

    // Pre-fill the prompt template modal with the prompt template
    const form = document.getElementById('savePromptForm');

    form.elements['Prompt'].value = prompt.Prompt;
    form.elements['Teaser'].value = prompt.Teaser;
    form.elements['PromptHint'].value = prompt.PromptHint;
    form.elements['Title'].value = prompt.Title;
    form.elements['Community'].value = prompt.Community;
    form.elements['ID'].value = prompt.ID;
    form.elements['AuthorName'].value = prompt.AuthorName;
    form.elements['AuthorURL'].value = prompt.AuthorURL;
    form.elements['Views'].value = prompt.Views;
    form.elements['Usages'].value = prompt.Usages;
    form.elements['Votes'].value = prompt.Votes;

    // Check the "Share as public" checkbox if the prompt template is public
    if (prompt.PromptTypeNo === PromptTypeNo.PUBLIC) {
      form.elements['Public'].checked = true;
    }

    // Trigger onchange event on Topics to update available Activities
    form.elements['Community'].dispatchEvent(new Event('change'));

    // Set the selected Activity (category)
    form.elements['Category'].value = prompt.Category;
  },

  // Delete a prompt template
  async deletePromptTemplate(idx) {
    const prompt =
      this.PromptTemplatesType === PromptTemplatesType.OWN
        ? this.OwnPrompts[idx]
        : this.PromptTemplates[idx];

    // Only allow deleting of own prompt templates
    if (
      this.PromptTemplatesType !== PromptTemplatesType.OWN &&
      !prompt.OwnPrompt &&
      !this.isAdminMode()
    ) {
      return;
    }

    // Ask for confirmation
    if (
      !confirm(
        `Are you sure you want to delete prompt template "${prompt.Title}"?`
      )
    ) {
      return;
    }

    try {
      await this.Client.deletePrompt(prompt.ID);

      // remove template using ID
      this.OwnPrompts = this.OwnPrompts.filter(
        (ownPrompt) => ownPrompt.ID !== prompt.ID
      );

      // remove template using ID from the public prompt templates if it's public
      if (prompt.PromptTypeNo === PromptTypeNo.PUBLIC) {
        this.PromptTemplates = this.PromptTemplates.filter(
          (promptTemplate) => promptTemplate.ID !== prompt.ID
        );
      }
    } catch (error) {
      this.showNotification(
        NotificationSeverity.ERROR,
        'Something went wrong. Please try again.'
      );
      return;
    }

    // update the section
    this.insertPromptTemplatesSection();
  },

  // Vote for a prompt template with a thumbs up
  async voteThumbsUp(idx) {
    try {
      await this.Client.voteForPrompt(this.PromptTemplates[idx].ID, 1);
    } catch (error) {
      this.showNotification(
        NotificationSeverity.ERROR,
        'Something went wrong. Please try again.'
      );
      return;
    }

    this.showNotification(
      NotificationSeverity.SUCCESS,
      'Thanks for your vote!'
    );
  },

  // Vote for a prompt template with a thumbs down
  async voteThumbsDown(idx) {
    try {
      await this.Client.voteForPrompt(this.PromptTemplates[idx].ID, -1);
    } catch (error) {
      this.showNotification(
        NotificationSeverity.ERROR,
        'Something went wrong. Please try again.'
      );
      return;
    }

    this.showNotification(
      NotificationSeverity.SUCCESS,
      'Thanks for your vote!'
    );
  },

  // Report the prompt template as inappropriate
  async reportPrompt(e) {
    // prevent the form from submitting
    e.preventDefault();

    const formData = new FormData(e.target);

    try {
      await this.Client.reportPrompt(
        formData.get('PromptID'),
        +formData.get('FeedbackTypeNo'),
        formData.get('FeedbackText'),
        formData.get('FeedbackContact')
      );
    } catch (error) {
      this.showNotification(
        NotificationSeverity.ERROR,
        'Something went wrong. Please try again.'
      );
      return;
    }

    this.showNotification(
      NotificationSeverity.SUCCESS,
      'Thanks for your feedback! We will review this prompt.'
    );

    this.hideModal('reportPromptModal');
  },

  // Copy link to prompt template to clipboard
  copyPromptDeepLink(idx) {
    const prompt =
      this.PromptTemplatesType === PromptTemplatesType.OWN
        ? this.OwnPrompts[idx]
        : this.PromptTemplates[idx];

    if (!prompt) {
      return;
    }

    const promptLink =
      prompt.PromptTypeNo === PromptTypeNo.PUBLIC
        ? `https://app.aiprm.com/prompts/${prompt.ID}`
        : `https://chat.openai.com/chat?${queryParamPromptID}=${prompt.ID}`;

    navigator.clipboard
      .writeText(promptLink)
      .then(
        // successfully copied
        () => {
          // Warning about prompt not shared as public
          if (prompt.PromptTypeNo !== PromptTypeNo.PUBLIC) {
            this.showNotification(
              NotificationSeverity.WARNING,
              'The link to the prompt template was copied to your clipboard.<br>This prompt is not shared as public. Only you can access it.'
            );

            return;
          }

          // Success - copied & public
          this.showNotification(
            NotificationSeverity.SUCCESS,
            'The link to the prompt template was copied to your clipboard.'
          );
        },
        // error - something went wrong (permissions?)
        () => {
          this.showNotification(
            NotificationSeverity.ERROR,
            'Something went wrong. Please try again.'
          );
        }
      );
  },

  // This function selects a prompt template using the index
  selectPromptTemplateByIndex(idx) {
    const templates =
      this.PromptTemplatesType === PromptTemplatesType.OWN
        ? this.OwnPrompts
        : this.PromptTemplates;

    // If there are no templates, skip
    if (!templates || !Array.isArray(templates)) return;

    this.selectPromptTemplate(templates[idx]);

    // Hide the "Continue Writing" button (prompt selected/new chat)
    this.hideContinueActionsButton();
  },

  /**
   * Select a prompt template and show it in the prompt input field
   *
   * @param {Prompt} template
   */
  selectPromptTemplate(template) {
    const textarea = document.querySelector('textarea');
    const parent = textarea.parentElement;
    let wrapper = document.createElement('div');
    wrapper.id = 'prompt-wrapper';
    if (parent.querySelector('#prompt-wrapper')) {
      wrapper = parent.querySelector('#prompt-wrapper');
    } else {
      parent.prepend(wrapper);
    }

    const url = new URL(window.location.href);

    if (template) {
      wrapper.innerHTML = /*html*/ `
        <span class="${css`tag`}" title="${sanitizeInput(template.Teaser)}">
          ${sanitizeInput(template.Title)}
        </span>

        ${
          template.AuthorURL && template.AuthorName
            ? /*html*/ `
              <span class="text-xs">by 
                <a href="${sanitizeInput(template.AuthorURL)}"
                  class="mx-1 underline" 
                  onclick="event.stopPropagation()"
                  rel="noopener noreferrer" target="_blank"
                  title="Created by">${sanitizeInput(template.AuthorName)}</a>
              </span>
            `
            : ''
        }`;

      textarea.placeholder = template.PromptHint;
      this.SelectedPromptTemplate = template;
      textarea.focus();

      this.Client.usePrompt(template.ID, UsageTypeNo.CLICK);

      // Update query param AIPRM_PromptID to the selected prompt ID
      if (url.searchParams.get(queryParamPromptID) === template.ID) {
        return;
      }

      url.searchParams.set(queryParamPromptID, template.ID);
    } else {
      wrapper.innerHTML = '';
      textarea.placeholder = '';
      this.SelectedPromptTemplate = null;

      // Remove query param AIPRM_PromptID
      if (!url.searchParams.get(queryParamPromptID)) {
        return;
      }

      url.searchParams.delete(queryParamPromptID);
    }

    // Push new URL to browser history
    window.history.pushState({}, '', url);
  },

  CSVToArray(strData, strDelimiter) {
    strDelimiter = strDelimiter || ',';
    var pattern = new RegExp(
      '(\\' +
        strDelimiter +
        '|\\r?\\n|\\r|^)' +
        '(?:"([^"]*(?:""[^"]*)*)"|' +
        '([^"\\' +
        strDelimiter +
        '\\r\\n]*))',
      'gi'
    );
    var data = [[]];
    var matches;
    while ((matches = pattern.exec(strData))) {
      var delimiter = matches[1];
      if (delimiter.length && delimiter !== strDelimiter) {
        data.push([]);
      }
      var value = matches[2]
        ? matches[2].replace(new RegExp('""', 'g'), '"')
        : matches[3];
      data[data.length - 1].push(value);
    }
    return data;
  },

  // get the topic label from the topic ID
  getTopicLabel(TopicID) {
    const topic = this.Topics.find((topic) => topic.ID === TopicID);

    if (!topic) {
      return '';
    }

    return topic.Label;
  },

  // get the activity label from the activity ID
  getActivityLabel(ActivityID) {
    const activity = this.Activities.find(
      (activity) => activity.ID === ActivityID
    );

    if (!activity) {
      return '';
    }

    return activity.Label;
  },

  // current user is admin
  isAdmin() {
    return this.Client.User.UserStatusNo === UserStatusNo.ADMIN;
  },

  // current user is admin and has enabled admin mode
  isAdminMode() {
    return this.isAdmin() && this.AdminMode;
  },

  // toggle admin mode and re-render prompt templates
  toggleAdminMode() {
    if (!this.isAdmin()) {
      return;
    }

    this.AdminMode = !this.AdminMode;

    this.insertPromptTemplatesSection();
  },

  // current user can create public or private prompt template
  canCreatePromptTemplate() {
    return (
      this.canCreatePublicPromptTemplate() ||
      this.canCreatePrivatePromptTemplate()
    );
  },

  // current user can create private prompt template
  canCreatePrivatePromptTemplate() {
    return this.isAdmin() || this.Client.User.MaxNewPrivatePromptsAllowed > 0;
  },

  // current user can create public prompt template
  canCreatePublicPromptTemplate() {
    return this.isAdmin() || this.Client.User.MaxNewPublicPromptsAllowed > 0;
  },

  // display notification with "cannot create public prompt template" error
  cannotCreatePublicPromptTemplateError() {
    this.showNotification(
      NotificationSeverity.WARNING,
      'You have a prompt with less than 5 upvotes live.<br><br>You can only create new public prompts if all your public prompts have more than 5 upvotes. <br><br> Please try again in a few seconds, in case you just unpublished or deleted another public prompt.',
      false
    );
  },

  // display notification with "cannot create private prompt template" error
  cannotCreatePrivatePromptTemplateError() {
    this.showNotification(
      NotificationSeverity.WARNING,
      "You can only create new private prompts if you didn't reach the limit of max. allowed private prompts. <br><br> Please try again in a few seconds, in case you just deleted another private prompt.",
      false
    );
  },

  // display notification with "cannot create any prompt template" (public nor private) error
  cannotCreatePromptTemplateError() {
    this.showNotification(
      NotificationSeverity.WARNING,
      "You can only create new public prompts if all your public prompts have more than 5 upvotes.<br><br>You can only create new private prompts if you didn't reach the limit of max. allowed private prompts. <br><br> Please try again in a few seconds, in case you just unpublished or deleted another public prompt, or deleted another private prompt.",
      false
    );
  },
};

window.AIPRM.init();
