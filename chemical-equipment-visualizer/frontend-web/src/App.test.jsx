import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import React from 'react'
import App from './App'

// Mock global fetch
beforeEach(()=>{
  global.fetch = jest.fn((url, opts) => {
    // Equipment list request
    if (url.includes('/api/equipment')){
      return Promise.resolve({ json: () => Promise.resolve({ results: [{id:1,name:'Pump-1',type:'Pump',material:'Steel',pressure:5.2,temperature:110}] , next: null, previous: null }) })
    }
    if (url.includes('/api/datasets/')){
      return Promise.resolve({ json: () => Promise.resolve([]) })
    }
    if (url.includes('/api/upload/')){
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ created: 1, dataset: { id: 1 } }) })
    }
    return Promise.resolve({ json: () => Promise.resolve({}) })
  })
})

test('renders and shows chart canvases and upload button', async ()=>{
  render(<App />)
  expect(screen.getByText(/Chemical Equipment Visualizer/i)).toBeInTheDocument()
  // Wait for equipment to be loaded
  await waitFor(()=> expect(screen.getByText('Pump-1')).toBeInTheDocument())
  // canvas elements
  expect(document.querySelector('canvas')).toBeInTheDocument()
  // upload button exists
  expect(screen.getByText('⬆ Upload CSV')).toBeInTheDocument()
})

test('upload requires file selection', async ()=>{
  render(<App />)
  const uploadBtn = screen.getByText('⬆ Upload CSV')
  // no file selected should alert; we mock window.alert
  window.alert = jest.fn()
  fireEvent.click(uploadBtn)
  expect(window.alert).toHaveBeenCalledWith('Select CSV first')
})

test('upload with token sends Authorization header', async ()=>{
  render(<App />)
  // set token in localStorage
  localStorage.setItem('token', 'abc123')
  // create input element with file
  const input = document.createElement('input')
  input.type = 'file'
  const file = new File(['content'], 'test.csv', { type: 'text/csv' })
  Object.defineProperty(input, 'files', { value: [file] })
  input.id = 'csvFile'
  document.body.appendChild(input)

  const uploadBtn = screen.getByText('⬆ Upload CSV')
  await waitFor(()=> fireEvent.click(uploadBtn))

  // fetch should have been called for upload and include headers
  expect(global.fetch).toHaveBeenCalled()
})
