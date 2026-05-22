import { api } from 'src/boot/axios';

export interface Page<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const crud = <T extends { id?: string }>(base: string) => ({
  list: (params?: Record<string, unknown>) =>
    api.get<Page<T>>(`/v1/${base}/`, { params }).then((r) => r.data),
  retrieve: (id: string) => api.get<T>(`/v1/${base}/${id}/`).then((r) => r.data),
  create: (body: Partial<T>) => api.post<T>(`/v1/${base}/`, body).then((r) => r.data),
  update: (id: string, body: Partial<T>) =>
    api.patch<T>(`/v1/${base}/${id}/`, body).then((r) => r.data),
  remove: (id: string) => api.delete(`/v1/${base}/${id}/`).then((r) => r.data),
});
