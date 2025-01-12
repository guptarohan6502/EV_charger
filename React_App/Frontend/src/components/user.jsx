import React, { useEffect, useState } from 'react';
import AppBar from './appbar';
import scrclogo from './scrclogo.png';

const UserDashboard = () => {
  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const response = await fetch('http://localhost:8000/user/get-transactions');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if (data.transactions) {
          const mappedTransactions = data.transactions.map(transaction => ({
            charger: transaction.Charger_ID,
            amount: transaction["Transaction_Amount(Rupees)"],
            time: new Date(transaction.Timestamp * 1000).toLocaleString('en-IN', {
              year: 'numeric',
              month: '2-digit',
              day: '2-digit',
              hour: '2-digit',
              minute: '2-digit',
              hour12: false,
            }),
          }));

          const last10Transactions = mappedTransactions.slice(-5).reverse();
          setTransactions(last10Transactions);
        } else {
          console.error('Error: No transactions found in the response');
        }
      } catch (error) {
        console.error('Error fetching transactions:', error);
      }
    };

    fetchTransactions();
  }, []);

  return (
      <div style={{ fontFamily: 'Arial, sans-serif', backgroundColor: '#1a1a1a', color: '#ffffff', minHeight: '100vh', padding: '20px' }}>
        {/* AppBar */}
        <AppBar />

        {/* User Info Section */}
        <div style={{ display: 'flex', alignItems: 'center', margin: '20px 0', borderBottom: '1px solid #444', paddingBottom: '10px' }}>
          <img src={scrclogo} alt="Logo" style={{ width: '80px', height: '80px', marginRight: '20px' }} />
          <div>
            <h2 style={{ margin: '0', fontSize: '20px' }}>Rohan Gupta</h2>
            <p style={{ margin: '5px 0', fontSize: '16px' }}>User ID: 7503</p>
          </div>
        </div>

        {/* Transactions Table */}
        <div>
          <h3 style={{ fontSize: '18px', textAlign: 'center', marginBottom: '10px', borderBottom: '1px solid #555', paddingBottom: '5px' }}>Last Transactions</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
            <tr>
              <th style={{ border: '1px solid #444', padding: '8px', backgroundColor: '#222', fontSize: '14px', textAlign: 'center' }}>Charger</th>
              <th style={{ border: '1px solid #444', padding: '8px', backgroundColor: '#222', fontSize: '14px', textAlign: 'center' }}>Amount</th>
              <th style={{ border: '1px solid #444', padding: '8px', backgroundColor: '#222', fontSize: '14px', textAlign: 'center' }}>Time</th>
            </tr>
            </thead>
            <tbody>
            {transactions.map((transaction, index) => (
                <tr key={index}>
                  <td style={{ border: '1px solid #444', padding: '6px', fontSize: '14px', textAlign: 'center' }}>{transaction.charger}</td>
                  <td style={{ border: '1px solid #444', padding: '6px', fontSize: '14px', textAlign: 'center' }}>{transaction.amount}</td>
                  <td style={{ border: '1px solid #444', padding: '6px', fontSize: '14px', textAlign: 'center' }}>{transaction.time}</td>
                </tr>
            ))}
            </tbody>
          </table>
        </div>
      </div>
  );
};

export default UserDashboard;
