const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";

function explainError(status, serverMessage) {
  // Ожидаемые ошибки (проверка данных, не найдено) — у них есть понятное
  // объяснение с сервера, показываем его как есть.
  if (status === 400 || status === 404 || status === 409) {
    return serverMessage || "Проверьте правильность введённых данных.";
  }
  // Всё остальное (500 и прочие нестандартные ситуации) — не показываем
  // технические детали, говорим про неизвестную ошибку.
  return "Произошла неизвестная ошибка. Попробуйте позже.";
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      ...options,
    });
  } catch (e) {
    // Запрос не дошёл до сервера: сеть, сервер не запущен или недоступен адрес.
    throw new Error("Нет связи с сервером. Проверьте, запущен ли бэкенд и верен ли его адрес.");
  }

  let data = null;
  try {
    data = await response.json();
  } catch (e) {
    data = null; // тело ответа — не JSON (например, страница ошибки)
  }

  if (!response.ok) {
    throw new Error(explainError(response.status, data && data.error));
  }
  return data;
}

export const api = {
  getTeachers: () => request("/teachers"),
  getClassrooms: () => request("/classrooms"),
  getLaptops: () => request("/laptops"),
  createIssue: (payload) => request("/issues", { method: "POST", body: JSON.stringify(payload) }),
  returnIssue: (issueId) => request(`/issues/${issueId}/return`, { method: "POST" }),
  releaseLaptop: (laptopId) => request(`/laptops/${laptopId}/release`, { method: "POST" }),
  getHistory: () => request("/history"),
};
