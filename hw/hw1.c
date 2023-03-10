#include <stdio.h>

double integrate(double (*f)(double),double a,double b) {
    // ...
    double sum=0;
    for (double i=a;i<=b;i+=0.00001){
        sum +=f(i)*0.00001;
    }
    return sum;

}

double square(double x) {
    return x*x;
}

int main() {
    printf("integrate(square, 0.0, 2.0)=%f\n", integrate(square, 0.0, 2.0));
}
/*
integrate(square, 0.0, 2.0)=2.666647
*/