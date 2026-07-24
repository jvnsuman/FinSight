import axiosClient from './axiosClient'

export const previewImport = (accountId, mapping, file) => {
  const formData = new FormData()
  formData.append('account_id', accountId)
  formData.append('mapping', JSON.stringify(mapping))
  formData.append('file', file)
  return axiosClient.post('/transactions/import/preview', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const commitImport = (accountId, rows) =>
  axiosClient.post('/transactions/import/commit', { account_id: accountId, rows })
