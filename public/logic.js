export const STORAGE_KEY = 'python-study-room-v1';
export function gradeQuestion(question, response = []) {
  const answers = Array.isArray(response) ? response : [];
  const expected = question.answers;
  const answered = question.type === 'slots' ? expected.every((_, i) => !!answers[i]) : answers.length > 0;
  const correct = question.type === 'slots'
    ? expected.every((value, i) => answers[i] === value) && answers.length === expected.length
    : answers.length === expected.length && new Set(answers).size === answers.length && expected.every(value => answers.includes(value));
  return { correct, answered, selected: answers, expected };
}
export function gradeExam(questions, responses) {
  const results = questions.map(question => ({question, ...gradeQuestion(question, responses[question.id])}));
  const correct = results.filter(result => result.correct).length;
  const unanswered = results.filter(result => !result.answered).length;
  return {results, correct, wrong: questions.length - correct - unanswered, unanswered, total: questions.length, percentage: questions.length ? Math.round(correct / questions.length * 100) : 0};
}
export function shuffle(items, random = Math.random) {
  const shuffled = [...items];
  for(let i=shuffled.length-1;i>0;i--){const j=Math.floor(random()*(i+1));[shuffled[i],shuffled[j]]=[shuffled[j],shuffled[i]];}
  return shuffled;
}
export function loadState(storage) {
  try {const value = JSON.parse(storage.getItem(STORAGE_KEY) || '{}');return value && typeof value === 'object' && !Array.isArray(value) ? value : {};}catch{return {};}
}
