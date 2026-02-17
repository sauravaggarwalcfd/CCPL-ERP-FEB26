import api from './api'

export const productService = {
  list: (params) =>
    api.get('/products', { params }).then(res => res.data),
  
  get: (id) =>
    api.get(`/products/${id}`).then(res => res.data),
  
  create: (data) =>
    api.post('/products', data).then(res => res.data),
  
  update: (id, data) =>
    api.put(`/products/${id}`, data).then(res => res.data),
  
  delete: (id) =>
    api.delete(`/products/${id}`).then(res => res.data)
}
