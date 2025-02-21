#include <iostream>

using namespace std;
int main(){
    int a = 10 ;
    // for (int i = 1; i <= a; i++)
    // {
    //     for (int j = 0; j < i - 1; j++)
    //     {
    //         cout << " ";
    //     }
    //     for (int k = a; k >= i; k--)
    //     {
    //         cout << "*";
    //     }
    //     cout << endl;
    // }

    // for (int i = 0; i < a; i++)
    // {
    //     for (int j = a; j > i +1; j--)
    //     {
    //         cout << " ";
    //     }
    //     for (int k = 0; k <= i; k++)
    //     {
    //         cout << "*";
    //     }
        
    //     cout << endl;
    // }
    int c = 0;
    for (int i = 0; i < a*2; i+=2)
    {

        for (int k = 0; k < c; k++)
        {
            cout << " ";
        }
        for (int j = i; j < (a*2)-1; j++)
        {
            cout << "*";
        }
        cout << endl;
        c++;
    }
    c = 3;
    for (int i = 0; i < a-1; i++)
    {
        for (int j = a-2; j > i; j--)
        {
            cout << " ";
        }

        for (int k = 0; k < c; k++)
        {
            cout << "*";
        }
        c+=2;
        cout << endl;
    }
    
    
    


    return 0;
}