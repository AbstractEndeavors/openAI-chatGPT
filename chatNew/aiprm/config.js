// Define global constants
const PromptPlaceholder = '[PROMPT]';
const TargetLanguagePlaceholder = '[TARGETLANGUAGE]';
const LanguageFeedURL = 'https://api.aiprm.com/csv/languages-20230119.csv?v=';
const TopicFeedURL = 'https://api.aiprm.com/csv/topics-20230123.csv?v=';
const ActivityFeedURL = 'https://api.aiprm.com/csv/activities-20230124.csv?v=';
const ToneFeedURL = 'https://api.aiprm.com/csv/tones-v2-20230216.csv?v=';
const WritingStyleFeedURL =
  'https://api.aiprm.com/csv/writing_styles-v2-20230216.csv?v=';
const ContinueActionsFeedURL =
  'https://api.aiprm.com/csv/continue_actions-20230216.csv?v=';
const EndpointConversation = 'https://chat.openai.com/backend-api/conversation';
const AppShort = 'AIPRM';
const AppName = 'AIPRM for ChatGPT';
const AppSlogan = 'AIPRM - ChatGPT Prompts';
const AppURL =
  'https://www.aiprm.com/?via=chatgpt&utm_campaign=users&utm_source=chatgpt&utm_medium=navlink&utm_content=AIPRM';
const ExportFilePrefix = 'AIPRM-export-chatgpt-thread_';
const ExportHeaderPrefix =
  '\n```\nExported with AIPRM https://www.aiprm.com by ';
const APIEndpoint = 'https://api.aiprm.com/api2';
// const APIEndpoint = 'http://localhost:8399';

export {
  PromptPlaceholder,
  TargetLanguagePlaceholder,
  LanguageFeedURL,
  EndpointConversation,
  AppShort,
  AppName,
  AppSlogan,
  AppURL,
  ExportFilePrefix,
  ExportHeaderPrefix,
  APIEndpoint,
  TopicFeedURL,
  ActivityFeedURL,
  ToneFeedURL,
  WritingStyleFeedURL,
  ContinueActionsFeedURL,
};
