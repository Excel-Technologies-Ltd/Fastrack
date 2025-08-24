import  { useState } from 'react';
import { Select, Card, Typography, Space } from 'antd';

const TestSearchable = () => {
  const [searchValue, setSearchValue] = useState('');
  const [selectedValue, setSelectedValue] = useState('');

  // Test options
  const testOptions = [
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' },
    { value: 'option3', label: 'Option 3' },
    { value: 'test1', label: 'Test 1' },
    { value: 'test2', label: 'Test 2' },
  ];

  return (
    <Card title="Test Ant Design Select Component" style={{ maxWidth: 600, margin: '0 auto' }}>
      <Space direction="vertical" style={{ width: '100%' }}>
        <div>
          <Typography.Text strong>Test Search</Typography.Text>
          <Select
            showSearch
            placeholder="Search options..."
            value={searchValue}
            onChange={(value: string) => {
              console.log('onChange called:', value);
              setSearchValue(value);
              setSelectedValue(value);
            }}
            onSearch={(value: string) => {
              console.log('onSearch called:', value);
              setSearchValue(value);
            }}
            filterOption={false}
            options={testOptions}
            style={{ width: '100%' }}
            notFoundContent={searchValue ? "No options found" : "Start typing to search..."}
          />
        </div>
        
        <div>
          <Typography.Text>Search Value: {searchValue}</Typography.Text>
          <br />
          <Typography.Text>Selected Value: {selectedValue}</Typography.Text>
        </div>
      </Space>
    </Card>
  );
};

export default TestSearchable;

