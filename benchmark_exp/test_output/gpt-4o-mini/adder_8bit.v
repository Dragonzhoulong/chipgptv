module adder_8bit (
    input [7:0] a, 
    input [7:0] b,
    input cin,
    output [7:0] sum,
    output SUM,
    output cout
);
    wire [7:0] carry;
    
    // Full adder logic for each bit
    assign sum[0] = a[0] ^ b[0] ^ cin;
    assign carry[0] = (a[0] & b[0]) | (cin & (a[0] ^ b[0]));
    
    assign sum[1] = a[1] ^ b[1] ^ carry[0];
    assign carry[1] = (a[1] & b[1]) | (carry[0] & (a[1] ^ b[1]));
    
    assign sum[2] = a[2] ^ b[2] ^ carry[1];
    assign carry[2] = (a[2] & b[2]) | (carry[1] & (a[2] ^ b[2]));
    
    assign sum[3] = a[3] ^ b[3] ^ carry[2];
    assign carry[3] = (a[3] & b[3]) | (carry[2] & (a[3] ^ b[3]));
    
    assign sum[4] = a[4] ^ b[4] ^ carry[3];
    assign carry[4] = (a[4] & b[4]) | (carry[3] & (a[4] ^ b[4]));
    
    assign sum[5] = a[5] ^ b[5] ^ carry[4];
    assign carry[5] = (a[5] & b[5]) | (carry[4] & (a[5] ^ b[5]));
    
    assign sum[6] = a[6] ^ b[6] ^ carry[5];
    assign carry[6] = (a[6] & b[6]) | (carry[5] & (a[6] ^ b[6]));
    
    assign sum[7] = a[7] ^ b[7] ^ carry[6];
    assign cout = (a[7] & b[7]) | (carry[6] & (a[7] ^ b[7]));
    
    // SUM is the most significant bit (MSB) of the sum
    assign SUM = sum[7];

endmodule