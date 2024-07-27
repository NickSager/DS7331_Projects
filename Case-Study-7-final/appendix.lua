-- appendix.lua
local code_chunks = {}

function CodeBlock(elem)
  table.insert(code_chunks, elem)
  return pandoc.RawBlock('markdown', '')
end

function Pandoc(doc)
  -- Create the appendix header
  local appendix = {
    pandoc.Header(2, "Appendix"),
    pandoc.Header(3, "Python Code")
  }
  
  -- Add all collected code chunks to the appendix
  for _, chunk in ipairs(code_chunks) do
    table.insert(appendix, chunk)
  end

  -- Add the appendix to the end of the document
  for _, block in ipairs(appendix) do
    table.insert(doc.blocks, block)
  end

  return doc
end
