const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";

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
    // Показываем текст ошибки от сервера; если его нет — код статуса.
    const detail = data && data.error
      ? data.error
      : `Сервер вернул ошибку ${response.status} (${response.statusText || "без описания"}).`;
    throw new Error(detail);
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
