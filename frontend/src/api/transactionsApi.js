import axiosClient from './axiosClient'

export const getTransactions = (filters = {}) => {
  const params = new URLSearchParams()
  if (filters.account_id) params.append('account_id', filters.account_id)
  if (filters.category_id) params.append('category_id', filters.category_id)
  if (filters.transaction_type) params.append('transaction_type', filters.transaction_type)
  if (filters.limit) params.append('limit', filters.limit)
  if (filters.offset) params.append('offset', filters.offset)
  const qs = params.toString()
  return axiosClient.get(`/transactions${qs ? `?${qs}` : ''}`)
}

// Pulls the user's ENTIRE transaction history by paging through /transactions
// (the backend caps a single request at 200 rows and defaults to just the
// most recent 50). Anything that needs full-history aggregation - e.g. the
// Monthly Report's opening balance and past-month lookups - must use this
// instead of getTransactions(), or older months silently come back empty.
export const getAllTransactions = async (filters = {}) => {
  const pageSize = 200
  let offset = 0
  let all = []
  while (true) {
    const res = await getTransactions({ ...filters, limit: pageSize, offset })
    const page = Array.isArray(res?.data) ? res.data : []
    all = all.concat(page)
    if (page.length < pageSize) break
    offset += pageSize
  }
  return all
}

export const createTransaction = (data) => axiosClient.post('/transactions', data)

export const updateTransaction = (transactionId, data) => axiosClient.put(`/transactions/${transactionId}`, data)

export const deleteTransaction = (transactionId) => axiosClient.delete(`/transactions/${transactionId}`)

// Downloads the server-generated Excel report (with real, native pie/bar
// charts) for the given month. month must be YYYY-MM - the backend
// accepts any date within the month. Returns the raw blob; the caller is
// responsible for turning it into a file download (see MonthlyReport.jsx).
export const downloadMonthlyReportExcel = (month) =>
  axiosClient.get('/transactions/report/excel', {
    params: { month: `${month}-01` },
    responseType: 'blob',
  })
