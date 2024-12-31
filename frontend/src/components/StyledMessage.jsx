import React from 'react';
import ReactMarkdown from 'react-markdown';

const StyledMessage = ({ message }) => {
  // Clean up any special characters and standardize formatting
  const cleanContent = (content) => {
    return content
      // Fix bullet points
      .replace(/[•⁠]+\s*⁠*/g, '• ')
      .replace(/\n[•⁠]+/g, '\n• ')
      // Fix numbered lists that might have extra spaces
      .replace(/\n\s*(\d+)\.\s+/g, '\n$1. ')
      // Standardize multiple newlines
      .replace(/\n{3,}/g, '\n\n')
      // Fix any dash-style lists
      .replace(/\n\s*[-–—]\s+/g, '\n- ');
  };

  // Shared typography styles
  const typographyStyles = {
    heading: "font-bold leading-tight tracking-tight",
    text: "leading-relaxed",
    lists: "space-y-1 leading-relaxed",
    code: "font-mono text-sm",
  };

  return (
    <div className={message.role === 'user' ? 'flex justify-end' : 'flex justify-start'}>
      <div className={`${
        message.role === 'user' ? '' : ''
      } rounded-lg px-3 py-2 max-w-2xl`}>
        <ReactMarkdown
          className="prose max-w-none"
          components={{
            // Headings
            h1: ({node, ...props}) => (
              <h1 className={`${typographyStyles.heading} text-xl mb-3`} {...props}/>
            ),
            h2: ({node, ...props}) => (
              <h2 className={`${typographyStyles.heading} text-lg mb-2`} {...props}/>
            ),
            h3: ({node, ...props}) => (
              <h3 className={`${typographyStyles.heading} text-base mb-2`} {...props}/>
            ),
           
            // Basic text
            p: ({node, ...props}) => (
              <p className={`${typographyStyles.text} mb-2`} {...props}/>
            ),
           
            // Lists
            ul: ({node, ...props}) => (
              <ul className={`${typographyStyles.lists} list-disc ml-4 mb-2`} {...props}/>
            ),
            ol: ({node, ...props}) => (
              <ol className={`${typographyStyles.lists} list-decimal ml-4 mb-2`} {...props}/>
            ),
            li: ({node, ...props}) => (
              <li className={typographyStyles.text} {...props}/>
            ),
           
            // Code blocks
            code: ({node, inline, ...props}) => (
              inline ?
                <code className={`${typographyStyles.code} rounded px-1 py-0.5`} {...props}/> :
                <code className={`${typographyStyles.code} block bg-gray-100 rounded p-2 mb-2 overflow-x-auto`} {...props}/>
            ),
           
            // Blockquotes
            blockquote: ({node, ...props}) => (
              <blockquote className="border-l-4 border-gray-200 pl-3 italic my-2" {...props}/>
            ),
           
            // Tables
            table: ({node, ...props}) => (
              <div className="overflow-x-auto mb-2">
                <table className="min-w-full divide-y divide-gray-200" {...props}/>
              </div>
            ),
            th: ({node, ...props}) => (
              <th className="px-2 py-1 bg-gray-50 font-semibold text-left" {...props}/>
            ),
            td: ({node, ...props}) => (
              <td className="px-2 py-1 border-t border-gray-100" {...props}/>
            ),
           
            // Links
            a: ({node, ...props}) => (
              <a className="text-blue-600 hover:underline" {...props}/>
            ),
           
            // Images
            img: ({node, ...props}) => (
              <img className="max-w-full h-auto rounded my-2" {...props}/>
            ),
           
            // Horizontal rule
            hr: ({node, ...props}) => (
              <hr className="my-4 border-t border-gray-200" {...props}/>
            ),
          }}
        >
          {cleanContent(message.content)}
        </ReactMarkdown>
      </div>
    </div>
  );
};

export default StyledMessage;